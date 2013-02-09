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
# Copyright 2012 Ben Nemec
# @End License@
from PyQt4.QtGui import QVBoxLayout, QDialog, QX11Info, QHBoxLayout, QProgressBar
from PyQt4.QtCore import Qt, QTimer
from MPlayer import MPlayer
from ScaledLabel import ScaledLabel

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
      
      
   def resizeEvent(self, event):
      textHeight = event.size().height() * .4
      self.timeBar.setStyleSheet('QProgressBar {font-size: %dpt;}' % textHeight)
      
      
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
      self.message = ScaledLabel()
      self.message.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
      self.message.setAttribute(Qt.WA_TranslucentBackground)
      self.layout.addWidget(self.message)
      
      
   def setMessage(self, message):
      self.message.setText(message)
      
      
class ChannelOverlay(MessageOverlay):
   def __init__(self, keyPressHandler, parent = None):
      MessageOverlay.__init__(self, keyPressHandler, parent)
      self.message = ScaledLabel(scale = 1.5)
      self.inputActive = False
      
      
   def numberPressed(self, number):
      if not self.inputActive:
         self.message.setText('')
      self.inputActive = True
      self.message.setText(self.message.text() + str(number))
      
      
   def hideEvent(self, event):
      self.message.setText('')
      self.inputActive = False
      