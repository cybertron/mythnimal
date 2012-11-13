from MenuItem import MenuItem
from PyQt4.QtGui import QLabel, QPalette, QColor, QHBoxLayout
from PyQt4.QtCore import Qt

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
      