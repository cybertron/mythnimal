from PyQt4.QtGui import QWidget, QLabel, QPalette, QColor, QHBoxLayout
from PyQt4.QtCore import Qt, pyqtSignal

class MenuItem(QWidget):
   """Base class for items that can be inserted into a MenuWidget"""
   selected = pyqtSignal()
   def __init__(self):
      QWidget.__init__(self)
      
      self.id = None
      
   def select(self):
      pass
   
   def deselect(self):
      pass
   
   
class SimpleMenuItem(MenuItem):
   def __init__(self, title):
      MenuItem.__init__(self)
      
      self.id = title
      self.layout = QHBoxLayout(self)
      self.label = QLabel(title)
      self.layout.addWidget(self.label)
      
      self.baseStyle = self.label.styleSheet()
      self.selectedStyle = 'QLabel { text-decoration: underline; }'
      self.focusedSelectedStyle = 'QLabel { font-weight: bold; text-decoration: underline; }'
      
      self.setMinimumHeight(25)
      
   def select(self, focus):
      if not focus:
         self.label.setStyleSheet(self.selectedStyle)
      else:
         self.label.setStyleSheet(self.focusedSelectedStyle)
      
   def deselect(self):
      self.label.setStyleSheet(self.baseStyle)
      
   
   
from MythDBObjects import Program

class ProgramMenuItem(MenuItem):
   def __init__(self, programData):
      MenuItem.__init__(self)
      
      self.programData = programData
      self.id = programData.basename
      
      self.layout = QHBoxLayout(self)
      
      text = programData.title
      if programData.subtitle != '':
         text += ' - ' + programData.subtitle
      self.programLabel = QLabel(text)
      self.layout.addWidget(self.programLabel)
      
      self.baseStyle = self.programLabel.styleSheet()
      self.focusedSelectedStyle = 'QLabel { font-weight: bold; text-decoration: underline; }'
      
      self.setMinimumHeight(25)
      
      
   def select(self, focus):
      if not focus:
         self.programLabel.setStyleSheet(self.baseStyle)
      else:
         self.programLabel.setStyleSheet(self.focusedSelectedStyle)
      
   def deselect(self):
      self.programLabel.setStyleSheet(self.baseStyle)