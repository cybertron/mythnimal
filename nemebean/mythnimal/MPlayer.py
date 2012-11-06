# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
import time, sys, os

class MPlayer(QObject):
   fileFinished = pyqtSignal()
   playbackStarted = pyqtSignal()
   foundAspect = pyqtSignal()
   foundVolume = pyqtSignal(int)
   foundPosition = pyqtSignal()

   @staticmethod
   def formatTime(time):
      hours = time / 3600
      tempTime = time - hours * 3600
      minutes = tempTime / 60
      seconds = tempTime - minutes * 60
      if hours > 0:
         return str(hours) + ':' + str(minutes).zfill(2) + ':' + str(seconds).zfill(2)
      else:
         return str(minutes).zfill(2) + ':' + str(seconds).zfill(2)

   def __init__(self, label, filename, extraOptions = ''):
      QObject.__init__(self)

      self.outputLabel = label
      self.extraOptions = extraOptions
      self.clear()
      self.logWidget = None
      self.lastVolume = time.time()
      self.lastVolumeValue = 0
      self.filename = filename

      self.process = QProcess()
      self.process.readyReadStandardOutput.connect(self.readStdout)
      self.process.finished.connect(self.finished)
      self.ensureRunning()
      
      self.infoProcess = QProcess()
      self.infoProcess.readyReadStandardOutput.connect(self.infoStdout)
      self.infoProcess.finished.connect(self.infoFinished)
      self.infoFinished()
      
      self.timer = QTimer()
      self.timer.setInterval(250)
      self.timer.timeout.connect(self.getVolume)
      self.timer.start()
      

   def play(self):
      if not self.inPlayback:
         return

      self.process.write("pause\n")
      self.playing = not self.playing


   def ensureRunning(self):
      wid = self.outputLabel.winId()
      # The int may help with hypothetical future Windows compatibility
      wid = str(int(wid))

      fullCommand = 'mplayer -slave -identify -quiet -osdlevel 0 -cache 25000 -cache-min 1 '
      fullCommand += ' -input nodefault-bindings:conf=' + os.devnull
      fullCommand += ' -wid ' + wid
      fullCommand += ' ' + self.extraOptions
      fullCommand += ' ' + self.filename
      if self.process.state() == QProcess.NotRunning:
         if self.logWidget:
            self.logWidget.append("MPlayer Command: " + fullCommand)
         print "MPlayer Command:", fullCommand
         self.process.start(fullCommand)


   def end(self):
      self.timer.stop()
      self.process.terminate()
      time.sleep(.1)
      self.process.kill()


   def seek(self, position):
      adjustedPosition = int(float(position) / self.seekScale)
      self.position = adjustedPosition
      self.process.write("pausing_keep_force seek " + str(adjustedPosition) + " 2\n")
      
      
   def seekRelative(self, amount):
      self.process.write('pausing_keep_force seek ' + str(amount) + '\n')


   def readStdout(self):
      lines = self.process.readAllStandardOutput().data().splitlines()
      for line in lines:
         # Don't spam the console with ANS_volume lines (we query it frequently)
         if line.find("ANS_volume=") != -1:
            val = int(float(line[11:]))
            # This can drive excessive CPU if we emit every time
            if (val != self.lastVolumeValue):
               self.foundVolume.emit(val)
               self.lastVolumeValue = val
            continue
         
         if line.startswith('ANS_time_pos'):
            parts = line.split('=')
            self.position = float(parts[1]) - self.startTime
            self.foundPosition.emit()
            continue
         
         if line.startswith('ANS_length'):
            parts = line.split('=')
            self.length = float(parts[1])
            
         # Not sure why this gets output so much, but it does so filter it out
         if line.startswith('PROGRAM_ID'):
            continue
         
         print "MPlayer:", line
         if self.logWidget:
            self.logWidget.append("MPlayer: " + line)
            
         if line.find("Starting playback...") != -1:
            self.timer.start() # Do this before setting inPlayback to eliminate any chance of a race condition
            self.lastVolume = time.time() # Ditto
            self.inPlayback = True
            self.playbackStarted.emit()

         if line.find("Title: ") != -1:
            foundTitle = line[8:]
            if foundTitle != "":
               self.title = foundTitle
            print "Found title:", self.title

         if line.find("Name: ") != -1:
            foundTitle = line[7:]
            if foundTitle != "":
               self.title = foundTitle
            print "Found title:", self.title

         if line.find("Artist:") != -1:
            foundArtist = line[9:]
            if foundArtist != "":
               self.artist = foundArtist
            print "Found artist:", self.artist

         if line.find("Album:") != -1:
            foundAlbum = line[8:]
            if foundAlbum != "":
               self.album = foundAlbum
            print "Found album:", self.album

         if line.find("ID_LENGTH=") != -1:
            self.length = int(float(line[10:]))

         if line.find("ID_VIDEO_WIDTH") != -1:
            self.width = int(line[15:])

         if line.find("ID_VIDEO_HEIGHT") != -1:
            self.height = int(line[16:])

         if line.find("ID_VIDEO_ASPECT") != -1:
            self.aspect = float(line[16:])
            self.foundAspect.emit()
            
         if line.startswith('ID_START_TIME'):
            self.startTime = float(line[14:])
            
         if line.startswith('ID_VIDEO_FPS'):
            self.fps = float(line[13:])

      sys.stdout.flush()


   def formattedTime(self, time = None):
      if time == None:
         time = self.length
      return MPlayer.formatTime(time)


   def clear(self):
      self.playing = True
      self.inPlayback = False
      self.title = "n/a"
      self.album = "n/a"
      self.artist = "n/a"
      self.length = 0
      self.seekScale = 1
      self.pending = 0
      self.aspect = 0
      self.position = 0


   def finished(self):
      self.clear()
      self.playing = False
      self.fileFinished.emit()
      
      
   def infoFinished(self):
      self.infoTimer = QTimer()
      self.infoTimer.setSingleShot(True)
      self.infoTimer.timeout.connect(self.startInfoProcess)
      self.infoTimer.start(1000)
      
      
   def startInfoProcess(self):
      fullCommand = 'mplayer -identify -quiet -frames 0 -vo null -ao null ' + self.filename
      self.infoProcess.start(fullCommand)
      
      
   def infoStdout(self):
      lines = self.infoProcess.readAllStandardOutput().data().splitlines()
      for line in lines:
         if line.find("ID_LENGTH=") != -1:
            self.length = int(float(line[10:]))

            
   def setVolume(self, vol):
      self.process.write("pausing_keep_force volume " + str(vol) + " 1\n")
      
      
   def getVolume(self):
      # This only works when we're playing
      if self.inPlayback:
         self.process.write('pausing_keep_force get_property volume\n')
         self.process.write('pausing_keep_force get_property time_pos\n')

