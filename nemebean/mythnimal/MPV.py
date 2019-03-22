# -*- coding: utf-8 -*-
# @Begin License@
# This file is part of Mythnimal.
#
# Mythnimal is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mythnimal is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mythnimal.  If not, see <http:#www.gnu.org/licenses/>.
#
# Copyright 2012, 2013 Ben Nemec
# @End License@

from Settings import settings
from PyQt4.QtCore import *
import time, sys, os, json, socket, Queue

class MPV(QObject):
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
      self.filename = filename
      self.fps = 0
      self.ended = False

      self.process = QProcess()
      self.process.readyReadStandardOutput.connect(self.readStdout)
      self.process.finished.connect(self.finished)
      self.ensureRunning()
      
      self.infoProcess = QProcess()
      self.infoProcess.readyReadStandardOutput.connect(self.infoStdout)
      self.infoProcess.finished.connect(self.infoFinished)
      self.infoFinished()
      
      self.timer = QTimer()
      self.timer.setInterval(10)
      self.timer.timeout.connect(self.handleEvents)
      self.timer.start()
      

   def play(self):
      self.sendCommand(['set_property', 'pause', self.playing])
      self.playing = not self.playing
      
   def setDeinterlacing(self, deinterlace):
      self.sendCommand(['set_property', 'deinterlace', deinterlace])


   def ensureRunning(self):
      wid = self.outputLabel.winId()
      # The int may help with hypothetical future Windows compatibility
      wid = str(int(wid))

      fullCommand = settings['mpv']
      fullCommand += ' --input-ipc-server=/tmp/mythnimal'
      fullCommand += ' --input-vo-keyboard=no'
      fullCommand += ' --wid=' + wid
      if settings['deinterlace']:
         fullCommand += ' --deinterlace=yes'
      else:
         fullCommand += ' --deinterlace=no'
      #fullCommand += ' ' + self.extraOptions
      fullCommand += ' ' + self.filename
      if self.process.state() == QProcess.NotRunning:
         print "MPV Command:", fullCommand
         self.process.start(fullCommand)


   def end(self):
      self.ended = True
      self.timer.stop()
      self.process.terminate()
      self.infoProcess.terminate()
      time.sleep(.1)
      self.process.kill()
      self.infoProcess.kill()


   def seek(self, position):
      """Seek to an absolute position"""
      adjustedPosition = int(float(position) / self.seekScale)
      self.position = adjustedPosition
      self.sendCommand(['seek', self.position, 'absolute'])
      
      
   def seekRelative(self, amount):
      """Seek relative to the current position"""
      print 'Seeking:', amount
      self.sendCommand(['seek', amount])
         
   
   def sendCommand(self, cmd):
      """Send a command to mpv
      
      cmd should be a list of objects representing the command and its parameters
      """
      self.openSocket()
      if self.socketReady():
         data = dict(command=cmd)
         command = json.dumps(data)
         #print command
         try:
            self.socket.send(command + '\n')
            self.commandQueue.put(cmd)
         except socket.error as e:
            if e.errno == 32:
               print 'MPV has gone away'
            else:
               raise
         
         
   def socketReady(self):
      return self.socket is not None
   
   def openSocket(self):
      if self.socketReady():
         return
      self.socket = socket.socket(socket.AF_UNIX)
      try:
         self.socket.connect('/tmp/mythnimal')
         print 'Connected to MPV socket'
      except socket.error as e:
         self.socket = None
         if e.errno == 111:
            print 'MPV not yet accepting connections.'
         else:
            raise
            
   
   def handleEvents(self):
      """Process events off the mpv socket"""
      self.openSocket()
      if not self.socketReady():
         return
      
      # Periodic status checks
      self.sendCommand(['get_property', 'time-pos'])
      
      # This should probably be done in a loop to get all of the available data,
      # but it turns out that can cause infinite loops when MPV ends.  Since this
      # function gets called repeatedly anyway and handles partial data, it should
      # be fine to do it this way.
      try:
         self.socketBuffer += self.socket.recv(4096, socket.MSG_DONTWAIT)
      except socket.error as e:
         if e.errno != 11:
            raise
      if not self.socketBuffer:
         return
      lines = self.socketBuffer.split('\n')
      for line in lines:
         #print line
         try:
            data = json.loads(line)
         except ValueError:
            # Don't try to process invalid json - it's probably a partial line that will
            # be handled the next time through
            continue
         event = data.get('event')
         error = data.get('error')
         if error:
            command = self.commandQueue.get()
            if error == 'success':
               self.handleCommand(command, data.get('data'))
            else:
               print 'MPV command "%s" failed due to "%s"' % (command, error)
         
      # If the last line was not completely received, put it back in the buffer
      if not self.socketBuffer.endswith('\n'):
         self.socketBuffer = lines[-1]
      else:
         self.socketBuffer = ''
         
         
   def handleCommand(self, command, data):
      if command == ['get_property', 'duration']:
         try:
            data = float(data)
         except ValueError:
            print 'Got bad length value:', data
            data = 0
         if data >= self.position:
            self.length = data
      elif command == ['get_property', 'time-pos']:
         self.position = data
         if self.position > self.length:
            self.length = self.position
         self.foundPosition.emit()
         if self.position > 0 and not self.inPlayback:
            self.inPlayback = True
            self.playbackStarted.emit()
            self.getFileInfo()
      elif command == ['get_property', 'width']:
         self.width = data
      elif command == ['get_property', 'height']:
         self.height = data
      elif command == ['get_property', 'video-params/aspect']:
         self.aspect = data
         self.foundAspect.emit()
      
      
   def getFileInfo(self):
      self.sendCommand(['get_property', 'width'])
      self.sendCommand(['get_property', 'height'])
      self.sendCommand(['get_property', 'video-params/aspect'])
      self.sendCommand(['get_property', 'duration'])


   def readStdout(self):
      lines = self.process.readAllStandardOutput().data().splitlines()
      for line in lines:
         print "MPV:", line

      sys.stdout.flush()


   def formattedTime(self, time = None):
      if time == None:
         time = self.length
      return MPlayer.formatTime(time)


   def clear(self):
      self.playing = True
      self.inPlayback = False
      self.length = 0
      self.seekScale = 1
      self.aspect = 0
      self.position = 0
      self.socket = None
      self.socketBuffer = ''
      self.commandQueue = Queue.Queue()


   def finished(self):
      self.clear()
      self.playing = False
      self.ended = True
      self.timer.stop()
      self.infoTimer.stop()
      self.fileFinished.emit()
      
      
   def infoFinished(self):
      if not self.ended:
         self.infoTimer = QTimer()
         self.infoTimer.setSingleShot(True)
         self.infoTimer.timeout.connect(self.startInfoProcess)
         self.infoTimer.start(1000)
      
      
   def startInfoProcess(self):
      fullCommand = '--term-playing-msg=length::${=duration} --vo=null --ao=null --frames=1 --quiet --no-cache --no-config -- ' + self.filename
      args = fullCommand.split()
      self.infoProcess.start(settings['mpv'], args)
      
      
   def infoStdout(self):
      lines = self.infoProcess.readAllStandardOutput().data().splitlines()
      for line in lines:
         if line.find("duration::") != -1:
            self.length = float(line.split('::')[1])
