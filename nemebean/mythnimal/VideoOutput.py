# -*- coding: iso-8859-1 -*-
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

from PyQt4.QtGui import QWidget, QGridLayout, QLabel, QSizePolicy, QRegion
from PyQt4.QtCore import QTimer, pyqtSignal, Qt

class VideoOutput(QWidget):
   readyForOverlay = pyqtSignal()
   def __init__(self, parent, keyHandler):
      QWidget.__init__(self, parent)

      self.keyPressHandler = keyHandler

      self.createUI()
      
      self.setMouseTracking(True)
      self.setWindowTitle("Mythnimal Video Output")
      
      
   def createUI(self):
      self.setStyleSheet('QWidget { background-color: black; }')
      
      self.videoLabel = VideoOutputLabel(self)

      
   def setSize(self, width, height):
      self.videoLabel.videoWidth = width
      self.videoLabel.videoHeight = height
      self.videoLabel.setSize(width, height)
      
      
   def resizeEvent(self, event):
      self.videoLabel.aspectResize(event.size().width(), event.size().height())
      self.readyForOverlay.emit()
      
      
   def setZoom(self, zoom):
      self.videoLabel.zoom = zoom
      self.videoLabel.aspectResize(self.width(), self.height())
      
   def nextZoom(self):
      newVal = (self.videoLabel.zoom + 1) % 4
      self.setZoom(newVal)
      return newVal
         
         
   def keyPressEvent(self, event):
      if not self.keyPressHandler(event):
         QWidget.keyPressEvent(self, event)


class VideoOutputLabel(QLabel):
   def __init__(self, parent = None):
      QWidget.__init__(self, parent)
      self.videoWidth = 1
      self.videoHeight = 1
      self.zoom = 0
      self.setMouseTracking(True)
      
   
   def setSize(self, width, height):
      self.setMinimumSize(width, height)
      self.setMaximumSize(width, height)
      self.resize(width, height)
      
      
   def aspectResize(self, width, height):
      if (float(width) / float(height) < float(self.videoWidth) / float(self.videoHeight)):
         newHeight = int(float(self.videoHeight * width) / self.videoWidth)
         self.setSize(width, newHeight)
         self.move(0, (height - newHeight) / 2)
      else:
         newWidth = int(float(self.videoWidth * height) / self.videoHeight)
         self.setSize(newWidth, height)
         self.move((width - newWidth) / 2, 0)
         
      if self.zoom == 1:
         self.applyZoom(1.1)
      if self.zoom == 2:
         self.applyZoom(1.2)
      if self.zoom == 3:
         self.applyZoom(1.25)
         
   def applyZoom(self, amount):
      newWidth = int(self.size().width() * amount)
      newHeight = int(self.size().height() * amount)
      moveX = self.pos().x() - (newWidth - self.size().width()) / 2
      moveY = self.pos().y() - (newHeight - self.size().height()) / 2
      self.setSize(newWidth, newHeight)
      self.move(moveX, moveY)


