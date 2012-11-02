# -*- coding: iso-8859-1 -*-

from PyQt4.QtGui import QWidget, QGridLayout, QLabel, QSizePolicy, QRegion, QPalette
from PyQt4.QtCore import QTimer, pyqtSignal, Qt

class VideoOutput(QWidget):
   readyForOverlay = pyqtSignal()
   def __init__(self, parent, keyHandler):
      QWidget.__init__(self, parent)

      self.fullscreen = False
      self.keyPressHandler = keyHandler
      self.frameHeight = 0

      self.createUI()
      
      self.setMouseTracking(True)
      self.setWindowTitle("Mythnimal Video Output")
      self.hide()
      
      
   def createUI(self):
      palette = QPalette()
      palette.setColor(QPalette.Background, Qt.black)
      self.setPalette(palette)
      self.setAutoFillBackground(True)
      
      self.videoLabel = VideoOutputLabel(self)

      
   def setSize(self, width, height):
      self.videoLabel.videoWidth = width
      self.videoLabel.videoHeight = height
      self.videoLabel.setSize(width, height)
      
      
   def resizeEvent(self, event):
      self.videoLabel.aspectResize(event.size().width(), event.size().height())
      self.readyForOverlay.emit()
      
      
   def setFitToWidth(self, fit):
      self.videoLabel.fitToWidth = fit
      self.videoLabel.aspectResize(self.width(), self.height())
         
         
   def keyPressEvent(self, event):
      if not self.keyPressHandler(event):
         QWidget.keyPressEvent(self, event)


class VideoOutputLabel(QLabel):
   def __init__(self, parent = None):
      QWidget.__init__(self, parent)
      self.videoWidth = 1
      self.videoHeight = 1
      self.fitToWidth = False
      self.setMouseTracking(True)
      
   
   def setSize(self, width, height):
      self.setMinimumSize(width, height)
      self.setMaximumSize(width, height)
      self.resize(width, height)
      
      
   def aspectResize(self, width, height):
      if (float(width) / float(height) < float(self.videoWidth) / float(self.videoHeight)) or self.fitToWidth:
         newHeight = int(float(self.videoHeight * width) / self.videoWidth)
         self.setSize(width, newHeight)
         self.move(0, (height - newHeight) / 2)
      else:
         newWidth = int(float(self.videoWidth * height) / self.videoHeight)
         self.setSize(newWidth, height)
         self.move((width - newWidth) / 2, 0)


