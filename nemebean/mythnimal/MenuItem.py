from PyQt4.QtGui import QWidget

class MenuItem(QWidget):
   """Base class for items that can be inserted into a MenuWidget"""
   def __init__(self):
      QWidget.__init__(self)
      
      self.id = None
      
   def select(self):
      pass
   
   def deselect(self):
      pass
   