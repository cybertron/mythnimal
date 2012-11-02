from MenuItem import MenuItem
from PyQt4.QtGui import QHBoxLayout, QLabel

class ProgramMenuItem(MenuItem):
   def __init__(self, programData):
      MenuItem.__init__(self)
      
      self.programData = programData
      self.id = programData[0]
      
      self.layout = QHBoxLayout(self)
      
      text = programData[1]
      if programData[2] != '':
         text += ' - ' + programData[2]
      self.programLabel = QLabel(text)
      self.layout.addWidget(self.programLabel)
      
      self.baseStyle = self.programLabel.styleSheet()
      self.selectedStyle = 'QLabel { background-color: blue; }'
      
      self.setMinimumHeight(25)
      
      
   def select(self):
      self.programLabel.setStyleSheet(self.selectedStyle)
      
   def deselect(self):
      self.programLabel.setStyleSheet(self.baseStyle)
      
      
      