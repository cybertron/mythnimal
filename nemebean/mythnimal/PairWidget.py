from PyQt4.QtGui import *

class PairWidget(QWidget):
   def __init__(self, label, widget, parent = None):
      QWidget.__init__(self, parent)
      
      self.layout = QHBoxLayout(self)
      self.layout.setContentsMargins(0, 0, 0, 0)
      
      self.label = label
      try:
         self.layout.addWidget(self.label)
      except:
         self.label = QLabel(label)
         self.layout.addWidget(self.label)
      
      self.widget = widget
      self.layout.addWidget(self.widget)