from MenuItem import MenuItem
from PyQt4.QtGui import QHBoxLayout, QLabel
from MythDB import Program

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
      self.selectedStyle = 'QLabel { background-color: blue; }'
      
      self.setMinimumHeight(25)
      
      
   def select(self):
      self.programLabel.setStyleSheet(self.selectedStyle)
      
   def deselect(self):
      self.programLabel.setStyleSheet(self.baseStyle)
      
      
      