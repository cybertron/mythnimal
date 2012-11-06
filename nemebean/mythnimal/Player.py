from PyQt4.QtCore import QObject, Qt, QTimer
from PyQt4.QtGui import QDialog, QHBoxLayout, QLabel, QProgressBar, QX11Info
from VideoOutput import VideoOutput
from MPlayer import MPlayer
from MythDB import Markup
import os

class Player(QObject):
   def __init__(self, x, y, filename, mythDB):
      QObject.__init__(self)
      
      self.filename = filename
      self.mythDB = mythDB
      
      self.getSkipList()
      
      self.videoOutput = VideoOutput(None, self.keyPressHandler)
      self.createOverlays()
      
      self.videoOutput.readyForOverlay.connect(self.placeOverlays)
      self.videoOutput.show()
      self.videoOutput.move(x, y)
      
      from MainForm import MainForm
      self.mplayer = MPlayer(self.videoOutput.videoLabel,
                             os.path.join(MainForm.settings['mythFileDir'], self.filename),
                             self.buildMPlayerOptions())
      self.mplayer.foundAspect.connect(self.setAspect)
      self.mplayer.foundPosition.connect(self.updatePosition)
      self.mplayer.fileFinished.connect(self.end)
      
      self.videoOutput.showFullScreen()
      
      
   def buildMPlayerOptions(self):
      opts = '-vf yadif '
      opts += '-framedrop ' # yadif can have problems keeping up on HD content
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
         self.end()
      elif key == Qt.Key_W:
         self.videoOutput.nextFitToWidth()
      elif key == Qt.Key_I:
         self.seekOverlay.showTimed()
      else:
         return False
      return True
      
      
   def seek(self, amount):
      self.seekOverlay.showTimed()
      self.mplayer.seekRelative(amount)
      
      
   def end(self):
      self.mplayer.end()
      self.videoOutput.hide()
      self.seekOverlay.hide()
      
      
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
         self.videoOutput.resize(1, 1)
         self.videoOutput.resize(self.videoOutput.width(), self.videoOutput.height())
         
         
   def updatePosition(self):
      self.seekOverlay.setTime(self.mplayer.position, self.mplayer.length)
      
      if self.nextSkip < len(self.starts):
         if self.mplayer.position > (float(self.starts[self.nextSkip]) / self.mplayer.fps):
            seekAmount = float(self.ends[self.nextSkip]) / self.mplayer.fps - self.mplayer.position
            print seekAmount
            self.mplayer.seekRelative(seekAmount)
            self.seekOverlay.showTimed()
            self.nextSkip += 1
         
         
   def createOverlays(self):
      self.seekOverlay = SeekOverlay(self.keyPressHandler, self.videoOutput)
      
   def placeOverlays(self):
      vidWidth = self.videoOutput.size().width()
      vidHeight = self.videoOutput.size().height()
      seekMargin = 20
      
      x = vidWidth / 2 + self.videoOutput.pos().x() - vidWidth / 2 + seekMargin
      y = vidHeight + self.videoOutput.pos().y() - self.seekOverlay.size().height() - seekMargin
      
      self.seekOverlay.resize(vidWidth - seekMargin * 2, self.seekOverlay.size().height())
      self.seekOverlay.move(x, y)
         
         
class SeekOverlay(QDialog):
   def __init__(self, keyPressHandler, parent = None):
      QDialog.__init__(self, parent)
      
      self.keyPressHandler = keyPressHandler
      
      self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
      # Causes issues in some non-compositing WM's (notably Fluxbox)
      if QX11Info.isCompositingManagerRunning():
         self.setAttribute(Qt.WA_TranslucentBackground)
         
      self.timer = QTimer()
      self.timer.setInterval(2000)
      self.timer.setSingleShot(True)
      self.timer.timeout.connect(self.hide)
      
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
      
      
   def showTimed(self):
      self.show()
      self.raise_()
      self.timer.start()
      
      
   def keyPressEvent(self, event):
      if not self.keyPressHandler(event):
         QDialog.keyPressEvent(self, event)