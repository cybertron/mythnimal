from PyQt4.QtCore import QObject, Qt, QTimer, pyqtSignal
from PyQt4.QtGui import QDialog, QHBoxLayout, QLabel, QProgressBar, QX11Info
from VideoOutput import VideoOutput
from MPlayer import MPlayer
from MythDBObjects import Markup
import os

class Player(QObject):
   finished = pyqtSignal()
   channelChange = pyqtSignal(str)
   def __init__(self, x, y, filename, mythDB):
      QObject.__init__(self)
      
      self.filename = filename
      self.mythDB = mythDB
      self.ended = False
      self.lastPosition = 0
      self.emitFinished = True
      self.currentChannel = None
      
      self.getSkipList()
      self.bookmark = self.mythDB.bookmark(self.filename)
      self.program = self.mythDB.getProgram(self.filename)
      self.recording = self.mythDB.programInUse(self.program)
      if self.recording:
         self.inUseTimer = QTimer()
         self.inUseTimer.setInterval(5000)
         self.inUseTimer.timeout.connect(self.checkRecording)
      
      self.videoOutput = VideoOutput(None, self.keyPressHandler)
      self.createOverlays()
      self.videoOutput.readyForOverlay.connect(self.placeOverlays)
      self.videoOutput.move(x, y)
      self.videoOutput.showFullScreen()
      
      self.startMPlayer()
      
   def startMPlayer(self, restarting = False):
      from MainForm import MainForm
      self.fullPath = os.path.join(MainForm.settings['mythFileDir'], self.filename)
      self.mplayer = MPlayer(self.videoOutput.videoLabel,
                             self.fullPath,
                             self.buildMPlayerOptions(restarting))
      self.mplayer.foundAspect.connect(self.setAspect)
      self.mplayer.foundPosition.connect(self.updatePosition)
      self.mplayer.fileFinished.connect(self.end)
      self.mplayer.playbackStarted.connect(self.playbackStarted)
      
      
   def buildMPlayerOptions(self, restarting):
      opts = '-osdlevel 0 -cache 25000 -cache-min 1 '
      opts += '-vf yadif '
      opts += '-framedrop ' # yadif can have problems keeping up on HD content
      if restarting:
         opts += '-ss ' + str(self.lastPosition - 5)
         print opts
      return opts
      
      
   def keyPressHandler(self, event):
      key = event.key()
      if key == Qt.Key_Space:
         self.mplayer.play()
         if not self.mplayer.playing:
            self.seekOverlay.show()
         else:
            self.seekOverlay.hide()
      elif key == Qt.Key_Left:
         self.seek(-5)
      elif key == Qt.Key_Right:
         self.seek(30)
      elif key == Qt.Key_Down:
         self.seek(-600)
      elif key == Qt.Key_Up:
         self.seek(600)
      elif key == Qt.Key_Escape:
         self.end(False)
      elif key == Qt.Key_W:
         zoom = self.videoOutput.nextZoom()
         if zoom == 0:
            self.showMessage('Zoom: Off')
         elif zoom == 1:
            self.showMessage('Zoom: 10%')
         elif zoom == 2:
            self.showMessage('Zoom: 20%')
         else:
            self.showMessage('Zoom: 25%')
      elif key == Qt.Key_I:
         self.seekOverlay.showTimed()
         if self.currentChannel is not None:
            self.channelOverlay.message.setText(self.currentChannel)
            self.channelOverlay.showTimed()
      # Making some assumptions about how Qt lays out its key structure, but that seems unlikely to change
      elif key >= Qt.Key_0 and key <= Qt.Key_9:
         self.channelOverlay.numberPressed(key - Qt.Key_0)
         self.channelOverlay.showTimed(3000)
      elif key == Qt.Key_Enter or key == Qt.Key_Return:
         self.channelChange.emit(self.channelOverlay.message.text())
         self.emitFinished = False
         self.end(False)
      else:
         return False
      return True
      
      
   def seek(self, amount):
      self.seekOverlay.showTimed()
      self.mplayer.seekRelative(amount)
      
      
   def end(self, eof = True):
      #  This gets called twice in some cases, but we only want to do it once
      if not self.ended:
         if eof and self.recording:
            print 'Restarting'
            self.startMPlayer(True)
            return
            
         self.mplayer.end()
         self.videoOutput.hide()
         self.seekOverlay.hide()
         self.messageOverlay.hide()
         self.channelOverlay.hide()
         self.mythDB.saveBookmark(self.mplayer, eof)
         self.ended = True
         if self.emitFinished:
            self.finished.emit()
      
      
      
   def getSkipList(self):
      skips = self.mythDB.skipList(self.filename)
      self.starts = skips[0]
      self.ends = skips[1]
      self.nextSkip = 0
      
      
      
   def setAspect(self):
      if self.mplayer.aspect > .0001:
         self.videoOutput.setSize(self.mplayer.aspect * 1000, 1000)
         # Need to trigger a resize event in order to make sure the video is resized correctly for the new aspect
         # Resize to same size won't do the trick
         width = self.videoOutput.width()
         height = self.videoOutput.height()
         self.videoOutput.resize(1, 1)
         self.videoOutput.resize(width, height)
         
   def playbackStarted(self):
      if self.bookmark > 0:
         # Ignore commercial skips prior to the bookmark
         if len(self.starts) > 0:
            while self.starts[self.nextSkip] < self.bookmark:
               self.nextSkip += 1
               
         self.mplayer.seek(int(float(self.bookmark) / self.mplayer.fps))
         self.bookmark = 0 # Don't do this again, even if we get the signal again
         
         
   def updatePosition(self):
      self.seekOverlay.setTime(self.mplayer.position, self.mplayer.length)
      if self.mplayer.length > self.lastPosition:
         self.lastPosition = self.mplayer.length
      
      if self.nextSkip < len(self.starts):
         start = float(self.starts[self.nextSkip]) / self.mplayer.fps
         end = float(self.ends[self.nextSkip]) / self.mplayer.fps
         if self.mplayer.position > start:
            seekAmount = end - self.mplayer.position
            self.seek(seekAmount)
            self.nextSkip += 1
            self.showMessage('Skipped ' + MPlayer.formatTime(int(end - start)))
         
         
   def createOverlays(self):
      self.seekOverlay = SeekOverlay(self.keyPressHandler, self.videoOutput)
      self.messageOverlay = MessageOverlay(self.keyPressHandler, self.videoOutput)
      self.channelOverlay = ChannelOverlay(self.keyPressHandler, self.videoOutput)
      
   def placeOverlays(self):
      vidWidth = self.videoOutput.size().width()
      vidHeight = self.videoOutput.size().height()
      seekMargin = 20
      
      x = vidWidth / 2 + self.videoOutput.pos().x() - vidWidth / 2 + seekMargin
      y = vidHeight + self.videoOutput.pos().y() - self.seekOverlay.size().height() - seekMargin
      
      self.seekOverlay.resize(vidWidth - seekMargin * 2, self.seekOverlay.size().height())
      self.seekOverlay.move(x, y)
      
      self.messageOverlay.resize(vidWidth / 2, vidHeight / 8)
      x = vidWidth / 2 + self.videoOutput.pos().x() - self.messageOverlay.size().width() / 2
      self.messageOverlay.move(x, self.videoOutput.pos().y() + seekMargin)
      
      self.channelOverlay.resize(vidWidth / 10, vidHeight / 10)
      x = self.videoOutput.pos().x() + vidWidth - self.channelOverlay.size().width() - seekMargin
      self.channelOverlay.move(x, self.videoOutput.pos().y() + seekMargin)
      
      
   def showMessage(self, message):
      self.messageOverlay.setMessage(message)
      self.messageOverlay.showTimed()
      
      
   def checkRecording(self):
      self.recording = self.mythDB.programInUse(self.program)
      if not self.recording:
         self.inUseTimer.stop() # No need to continue checking once it has stopped
         
      
      
from PyQt4.QtGui import QVBoxLayout
class Overlay(QDialog):
   def __init__(self, keyPressHandler, parent = None):
      QDialog.__init__(self, parent)
      
      self.keyPressHandler = keyPressHandler
      
      self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
      # Causes issues in some non-compositing WM's (notably Fluxbox)
      if QX11Info.isCompositingManagerRunning():
         self.setAttribute(Qt.WA_TranslucentBackground)
         
      self.timer = QTimer()
      self.timer.setSingleShot(True)
      self.timer.timeout.connect(self.hide)
      
      
   def showTimed(self, interval = 2000):
      self.show()
      self.raise_()
      self.timer.start(interval)
      
   def keyPressEvent(self, event):
      if not self.keyPressHandler(event):
         QDialog.keyPressEvent(self, event)
      
      
class SeekOverlay(Overlay):
   def __init__(self, keyPressHandler, parent = None):
      Overlay.__init__(self, keyPressHandler, parent)
      
      self.setupUI()
      
      
   def setupUI(self):
      self.layout = QHBoxLayout(self)
      
      self.timeBar = QProgressBar()
      self.layout.addWidget(self.timeBar)
      
      
   def setTime(self, current, total):
      current = int(current)
      total = int(total)
      self.timeBar.setMaximum(total)
      self.timeBar.setValue(current)
      self.timeBar.setFormat(MPlayer.formatTime(current) + '/' + MPlayer.formatTime(total))
      
      
class MessageOverlay(Overlay):
   def __init__(self, keyPressHandler, parent = None):
      Overlay.__init__(self, keyPressHandler, parent)
      
      self.layout = QVBoxLayout(self)
      self.message = QLabel()
      self.message.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
      self.message.setAttribute(Qt.WA_TranslucentBackground)
      self.layout.addWidget(self.message)
      
      
   def setMessage(self, message):
      self.message.setText(message)
      
      
class ChannelOverlay(MessageOverlay):
   def __init__(self, keyPressHandler, parent = None):
      MessageOverlay.__init__(self, keyPressHandler, parent)
      
      
   def numberPressed(self, number):
      self.message.setText(self.message.text() + str(number))
      
      
   def hideEvent(self, event):
      self.message.setText('')
      