from PyQt4.QtGui import QDialog, QHBoxLayout, QVBoxLayout, QLabel, QWidget
from PyQt4.QtCore import Qt, pyqtSignal
import datetime

class ChannelGuide(QDialog):
   def __init__(self, startChannel, mythDB, parent = None):
      QDialog.__init__(self, parent)
      self.mythDB = mythDB
      self.visibleChannels = 10
      self.startTime = datetime.datetime.today()
      
      self.channels = self.mythDB.getAllChannels()
      
      chan = [i for i in self.channels if i.channum == startChannel][0]
      self.selectedChannel = self.channels.index(chan)
      
      self.setupUI()
      
      self.refreshDisplay()
      
      
   def setupUI(self):
      self.mainLayout = QHBoxLayout(self)
      
      self.channelWidget = QWidget()
      self.mainLayout.addWidget(self.channelWidget, 3)
      self.channelLayout = QHBoxLayout(self.channelWidget)
      
      self.infoLayout = QVBoxLayout()
      self.mainLayout.addLayout(self.infoLayout, 1)
      
      self.programTitle = QLabel('Title')
      self.infoLayout.addWidget(self.programTitle)
      self.programSubtitle = QLabel('Subtitle')
      self.infoLayout.addWidget(self.programSubtitle)
      self.programDescription = QLabel('Description')
      self.infoLayout.addWidget(self.programDescription)
      
      
   def keyPressEvent(self, event):
      key = event.key()
      if key == Qt.Key_Escape:
         self.hide()
      elif key == Qt.Key_Up:
         self.selectedChannel -= 1
         self.validateSelected()
         self.refreshDisplay()
      elif key == Qt.Key_Down:
         self.selectedChannel += 1
         self.validateSelected()
         self.refreshDisplay()
      else:
         QDialog.keyPressEvent(self, event)
         
         
   def validateSelected(self):
      if self.selectedChannel < 0:
         self.selectedChannel += len(self.channels)
      self.selectedChannel %= len(self.channels)
         
         
   def refreshDisplay(self):
      startChanIndex = self.selectedChannel - self.visibleChannels / 2
      if startChanIndex < 0:
         startChanIndex += len(self.channels)
      endChanIndex = startChanIndex + self.visibleChannels
      
      endTime = self.startTime + datetime.timedelta(hours = 2)
      
      QWidget().setLayout(self.channelLayout)
      self.channelLayout = QVBoxLayout(self.channelWidget)
      
      for i in range(startChanIndex, endChanIndex):
         wrappedI = i % len(self.channels)
         chanId = self.channels[wrappedI].chanid
         selectedPrograms = self.mythDB.getProgramSchedule(chanId, self.startTime, endTime)
         
         layout = QHBoxLayout()
         self.channelLayout.addLayout(layout)
         layout.addWidget(GuideItem(str(self.channels[wrappedI].channum)))
         
         for j in selectedPrograms:
            layout.addWidget(GuideItem(j.title))
            
            
class GuideItem(QLabel):
   selected = pyqtSignal()
   def __init__(self, text = ''):
      QLabel.__init__(self, text)
      
      self.selectedStyle = 'QLabel {border: 3px solid white; font-size: 30pt}'
      self.normalStyle = 'QLabel {border: 1px solid white; font-size: 30pt}'
      self.setStyleSheet(self.normalStyle)
      
      
   def select(self):
      self.setStyleSheet(self.selectedStyle)
   
   def deselect(self):
      self.setStyleSheet(self.normalStyle)