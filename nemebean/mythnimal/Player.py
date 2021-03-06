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
from PyQt5.QtCore import QObject, Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QProgressBar
from VideoOutput import VideoOutput
from MPlayer import MPlayer
from MPV import MPV
from MythDBObjects import Markup
from Overlays import *
from ChannelGuide import ChannelGuide
from Settings import settings
import os

class Player(QObject):
   finished = pyqtSignal(bool)
   channelChange = pyqtSignal(str)
   seekedPastStart = pyqtSignal()
   toggleRecording = pyqtSignal()
   def __init__(self, x, y, filename, mythDB, startAtEnd = False):
      QObject.__init__(self)
      
      self.filename = filename
      self.mythDB = mythDB
      self.startAtEnd = startAtEnd
      self.ended = False
      self.lastPosition = 0
      self.emitFinished = True
      self.currentChannel = None
      self.previousChannel = None
      self.guide = None
      self.commskip = True
      
      self.getSkipList()
      self.bookmark = self.mythDB.bookmark(self.filename)
      self.program = self.mythDB.getProgram(self.filename)
      self.recording = self.mythDB.programInUse(self.program)
      
      self.videoOutput = VideoOutput(None, self.keyPressHandler)
      self.videoOutput.setWindowTitle(self.program.title)
      self.createOverlays()
      self.videoOutput.readyForOverlay.connect(self.placeOverlays)
      self.videoOutput.move(x, y)
      if settings['fullscreen']:
         self.videoOutput.showFullScreen()
      else:
         self.videoOutput.show()
      
      self.startBackend()
      
   def startBackend(self, restarting = False):
      if restarting:
         self.startAtEnd = True
      
      self.fullPath = os.path.join(settings['mythFileDir'], self.filename)
      #self.backend = VLC(self.videoOutput.videoLabel,
      #                   self.fullPath)
      mpv = True
      if not mpv:#settings['backend'] == 'mplayer':
         self.backend = MPlayer(self.videoOutput.videoLabel,
                             self.fullPath,
                             self.buildMPlayerOptions())
      else:
         self.backend = MPV(self.videoOutput.videoLabel,
                             self.fullPath,
                             self.buildMPlayerOptions())
      self.backend.foundAspect.connect(self.setAspect)
      self.backend.foundPosition.connect(self.updatePosition)
      self.backend.fileFinished.connect(self.end)
      self.backend.playbackStarted.connect(self.playbackStarted)
      
      
   def buildMPlayerOptions(self):
      opts = '-osdlevel 0 '
      # This causes issues seeking in files that are recording
      #opts += '-cache 25000 -cache-min 1 '
      if settings['deinterlace']:
         opts += '-vf yadif '
      opts += '-framedrop ' # yadif can have problems keeping up on HD content
      # TODO: Make language configurable
      opts += '-alang eng '
      return opts
      
      
   def keyPressHandler(self, event):
      key = event.key()
      if key == Qt.Key_Space:
         self.backend.play()
         if not self.backend.playing:
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
         print self.seekOverlay.pos(), self.seekOverlay.size()
         if self.currentChannel is not None:
            self.channelOverlay.message.setText(self.currentChannel)
            self.channelOverlay.showTimed()
      # Making some assumptions about how Qt lays out its key structure, but that seems unlikely to change
      elif key >= Qt.Key_0 and key <= Qt.Key_9:
         self.channelOverlay.numberPressed(key - Qt.Key_0)
         self.channelOverlay.showTimed(3000)
      elif key == Qt.Key_Underscore:
         self.channelOverlay.numberPressed(event.text())
      elif key == Qt.Key_Enter or key == Qt.Key_Return:
         channel = self.channelOverlay.message.text()
         self.changeChannel(channel)
      elif key == Qt.Key_Backspace:
         if self.previousChannel is not None:
            self.changeChannel(self.previousChannel)
         elif self.currentChannel is None:
            self.seekToLastCommercialStart()
      elif key == Qt.Key_D:
         settings['deinterlace'] = not settings['deinterlace']
         if settings['backend'] == 'mplayer':
            self.setBookmarkSeconds(self.backend.position)
            self.startBackend()
         else:
            self.backend.setDeinterlacing(settings['deinterlace'])
         if settings['deinterlace']:
            self.showMessage('Deinterlacing On')
         else:
            self.showMessage('Deinterlacing Off')
      elif key == Qt.Key_S:
         self.commskip = not self.commskip
         if self.commskip:
            self.showMessage('Skipping Commercials')
         else:
            self.showMessage('Not Skipping Commercials')
      elif key == Qt.Key_G:
         if self.currentChannel is not None:
            self.guide = ChannelGuide(self.currentChannel, self.mythDB, self.videoOutput)
            self.guide.channelSelected.connect(self.changeChannel)
            self.guide.showFullScreen()
            self.guide.raise_()
      elif key == Qt.Key_R:
         if self.currentChannel is not None:
            self.toggleRecording.emit()
      else:
         return False
      return True

      
   def seek(self, amount):
      if self.backend.position + amount < 0:
         self.seekedPastStart.emit()
      self.seekOverlay.showTimed()
      self.backend.seekRelative(amount)
      
      
   def end(self, eof = True):
      #  This gets called twice in some cases, but we only want to do it once
      if not self.ended:
         self.checkRecording()
         if eof and self.recording:
            print 'Restarting'
            self.startBackend(True)
            return
            
         self.backend.end()
         self.videoOutput.hide()
         self.seekOverlay.hide()
         self.messageOverlay.hide()
         self.channelOverlay.hide()
         if self.guide:
            self.guide.hide()
         self.mythDB.saveBookmark(self.backend, eof)
         self.ended = True
         if self.emitFinished:
            self.finished.emit(eof)
            
            
   def changeChannel(self, channel):
      self.emitFinished = False
      self.end(False)
      self.channelChange.emit(channel)
      
      
      
   def getSkipList(self):
      (self.starts, self.ends, self.mythRate) = self.mythDB.skipList(self.filename)
      self.nextSkip = 0
      
      
   def setAspect(self):
      if self.backend.aspect > .0001:
         # Set output to correct aspect, which will be respected by future
         # resize events.
         self.videoOutput.setSize(self.backend.aspect * 1000, 1000)
         # Need to trigger a resize event in order to make sure the video is resized correctly for the new aspect
         # Resize to same size won't do the trick
         if settings['fullscreen']:
            width = self.videoOutput.width()
            height = self.videoOutput.height()
         else:
            width = self.backend.width
            height = self.backend.height
         self.videoOutput.resize(1, 1)
         self.videoOutput.resize(width, height)
         
   
   def getRate(self):
      """ Myth sometimes reports a different framerate than MPlayer, and that
          screws up our calculations.  Use this function to select the best
          available rate.
      """
      rate = self.mythRate
      if rate is None:
         return self.backend.fps
      return self.mythRate
   
   
   def getTime(self, time):
      return float(time) / float(self.getRate())

      
   def commStartTime(self, i = None):
      if i is None:
         i = self.nextSkip
      return self.getTime(self.starts[i])
      
   def commEndTime(self, i = None):
      if i is None:
         i = self.nextSkip
      return self.getTime(self.ends[i])
      
   def bookmarkTime(self):
      return self.getTime(self.bookmark)
      
   def playbackStarted(self):
      if self.startAtEnd:
         self.setBookmarkSeconds(self.backend.length - 5)
         self.startAtEnd = False
         
      if self.bookmarkTime() > 0:
         # Ignore commercial skips prior to the bookmark
         startLen = len(self.starts)
         if startLen > 0:
            while self.nextSkip < startLen and self.commStartTime() < self.bookmarkTime():
               self.nextSkip += 1
               
         self.backend.seekRelative(int(self.bookmarkTime()))
         self.bookmark = 0 # Don't do this again, even if we get the signal again
         
   def updatePosition(self):
      self.seekOverlay.setTime(self.backend.position, self.backend.length)
      if self.backend.length > self.lastPosition:
         self.lastPosition = self.backend.length
      
      if self.nextSkip < len(self.starts):
         start = self.commStartTime()
         end = self.commEndTime()
         if self.backend.position > start:
            message = 'Would have skipped %s'
            if self.commskip:
               seekAmount = end - self.backend.position
               self.seek(seekAmount)
               message = 'Skipped %s'
            self.nextSkip += 1
            self.showMessage(message % MPlayer.formatTime(int(end - start)))
            
   def seekToLastCommercialStart(self):
      previous = self.nextSkip - 1
      if previous >= 0 and previous < len(self.starts):
         seekAmount = self.commStartTime(previous) - self.backend.position
         self.seek(seekAmount)
         
         
   def createOverlays(self):
      self.seekOverlay = SeekOverlay(self.keyPressHandler, self.videoOutput)
      self.seekOverlay.shown.connect(self.placeOverlays)
      self.messageOverlay = MessageOverlay(self.keyPressHandler, self.videoOutput)
      self.messageOverlay.shown.connect(self.placeOverlays)
      self.channelOverlay = ChannelOverlay(self.keyPressHandler, self.videoOutput)
      self.channelOverlay.shown.connect(self.placeOverlays)
      
   def placeOverlays(self):
      vidWidth = self.videoOutput.size().width()
      vidHeight = self.videoOutput.size().height()
      seekMargin = 20
      seekHeight = vidHeight / 15
      
      self.seekOverlay.resize(vidWidth - seekMargin * 2, seekHeight)
      x = vidWidth / 2 + self.videoOutput.pos().x() - vidWidth / 2 + seekMargin
      y = vidHeight + self.videoOutput.pos().y() - self.seekOverlay.size().height() - seekMargin
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
      
      
   def setBookmarkSeconds(self, seconds):
      self.bookmark = int(float(seconds) * self.getRate())

