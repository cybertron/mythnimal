from MenuItem import MenuItem
from PyQt4.QtGui import QLabel, QPalette, QColor
from PyQt4.QtCore import Qt

class ShowMenuItem(MenuItem):
   def __init__(self, title):
      MenuItem.__init__(self)
      
      self.id = title
      self.label = QLabel(title, self)
      self.baseStyle = self.label.styleSheet()
      self.selectedStyle = 'QLabel { background-color: blue; }'
      
      self.setMinimumHeight(25)
      
   def select(self):
      self.label.setStyleSheet(self.selectedStyle)
      
   def deselect(self):
      self.label.setStyleSheet(self.baseStyle)
      