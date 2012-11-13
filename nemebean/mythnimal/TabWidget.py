from PyQt4.QtGui import QTabWidget, QWidget

class TabWidget(QTabWidget):
   def __init__(self, parent = None):
      QTabWidget.__init__(self, parent)
      
   def createTab(self, name):
      widget = QWidget()
      self.addTab(widget, name)
      return widget