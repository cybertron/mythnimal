from PyQt4.QtGui import QVBoxLayout, QDialog, QX11Info, QHBoxLayout, QProgressBar, QLabel
from PyQt4.QtCore import Qt, QTimer
from MPlayer import MPlayer

class Overlay(QDialog):
   def __init__(self, keyPressHandler, parent = None):
      QDialog.__init__(self, parent)
      
      self.keyPressHandler = keyPressHandler
      
      self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
      # Causes issues in some non-compositing WM's (notably Fluxbox)
      if QX11Info.isCompositingManagerRunning():
         self.setAttribute(Qt.WA_TranslucentBackground)
         
      self.timer = QTimer()
      self.timer.setSingleShot(True)
      self.timer.timeout.connect(self.hide)
      
      
   def showTimed(self, interval = 2000):
      self.show()
      self.raise_()
      self.timer.start(interval)
      
   def keyPressEvent(self, event):
      if not self.keyPressHandler(event):
         QDialog.keyPressEvent(self, event)
      
      
class SeekOverlay(Overlay):
   def __init__(self, keyPressHandler, parent = None):
      Overlay.__init__(self, keyPressHandler, parent)
      
      self.setupUI()
      
      
   def setupUI(self):
      self.layout = QHBoxLayout(self)
      
      self.timeBar = QProgressBar()
      self.layout.addWidget(self.timeBar)
      
      
   def setTime(self, current, total):
      current = int(current)
      total = int(total)
      self.timeBar.setMaximum(total)
      self.timeBar.setValue(current)
      self.timeBar.setFormat(MPlayer.formatTime(current) + '/' + MPlayer.formatTime(total))
      
      
class MessageOverlay(Overlay):
   def __init__(self, keyPressHandler, parent = None):
      Overlay.__init__(self, keyPressHandler, parent)
      
      self.layout = QVBoxLayout(self)
      self.message = QLabel()
      self.message.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
      self.message.setAttribute(Qt.WA_TranslucentBackground)
      self.layout.addWidget(self.message)
      
      
   def setMessage(self, message):
      self.message.setText(message)
      
      
class ChannelOverlay(MessageOverlay):
   def __init__(self, keyPressHandler, parent = None):
      MessageOverlay.__init__(self, keyPressHandler, parent)
      
      
   def numberPressed(self, number):
      self.message.setText(self.message.text() + str(number))
      
      
   def hideEvent(self, event):
      self.message.setText('')
      