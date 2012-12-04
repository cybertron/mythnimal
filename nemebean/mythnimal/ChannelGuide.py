from PyQt4.QtGui import QDialog, QHBoxLayout, QVBoxLayout, QLabel, QWidget, QSizePolicy
from PyQt4.QtCore import Qt, pyqtSignal
import datetime

class ChannelGuide(QDialog):
   channelSelected = pyqtSignal(str)
   def __init__(self, startChannel, mythDB, parent = None):
      QDialog.__init__(self, parent)
      self.mythDB = mythDB
      self.visibleChannels = 11
      self.startTime = datetime.datetime.today().replace(second = 0, microsecond = 0)
      if self.startTime.minute >= 30:
         self.startTime = self.startTime.replace(minute = 30)
      else:
         self.startTime = self.startTime.replace(minute = 0)
      self.selectedStartTime = self.startTime
      self.displayLength = datetime.timedelta(hours = 2)
      
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
      
      self.programTitle = self.createLabel('Title')
      self.infoLayout.addWidget(self.programTitle)
      self.programSubtitle = self.createLabel('Subtitle')
      self.infoLayout.addWidget(self.programSubtitle)
      self.programDescription = self.createLabel('Description')
      self.programDescription.setStyleSheet('QLabel {font-size: 20pt}')
      self.infoLayout.addWidget(self.programDescription, 1)
      
   def createLabel(self, text):
      label = QLabel(text)
      label.setWordWrap(True)
      label.setStyleSheet('QLabel {font-size: 30pt}')
      return label
      
      
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
      elif key == Qt.Key_Right:
         self.nextTime()
      elif key == Qt.Key_Left:
         self.previousTime()
      elif key == Qt.Key_Enter or key == Qt.Key_Return:
         self.hide()
         self.channelSelected.emit(self.channels[self.selectedChannel].channum)
      else:
         QDialog.keyPressEvent(self, event)
         
         
   def validateSelected(self):
      if self.selectedChannel < 0:
         self.selectedChannel += len(self.channels)
      self.selectedChannel %= len(self.channels)
      
      
   def nextTime(self):
      self.selectedStartTime = self.selectedItem.program.endtime
      while self.selectedStartTime >= self.startTime + self.displayLength:
         self.startTime += datetime.timedelta(minutes = 30)
      self.refreshDisplay()
      pass
   
   def previousTime(self):
      self.selectedStartTime -= datetime.timedelta(minutes = 1)
      if self.selectedStartTime < self.startTime:
         self.startTime -= datetime.timedelta(minutes = 30)
      self.refreshDisplay()
      pass
         
         
   def refreshDisplay(self):
      startChanIndex = self.selectedChannel - self.visibleChannels / 2
      if startChanIndex < 0:
         startChanIndex += len(self.channels)
      endChanIndex = startChanIndex + self.visibleChannels
      
      endTime = self.startTime + self.displayLength
      
      QWidget().setLayout(self.channelLayout)
      self.channelLayout = QVBoxLayout(self.channelWidget)
      
      # Don't use rawI directly
      for rawI in range(startChanIndex, endChanIndex):
         wrappedI = rawI % len(self.channels)
         chanId = self.channels[wrappedI].chanid
         selectedPrograms = self.mythDB.getProgramSchedule(chanId, self.startTime, endTime)
         
         layout = QHBoxLayout()
         self.channelLayout.addLayout(layout)
         newItem = GuideItem(str(self.channels[wrappedI].channum))
         newItem.setMaximumWidth(125)
         newItem.setMinimumWidth(125)
         newItem.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Ignored)
         newItem.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
         layout.addWidget(newItem)
         
         if len(selectedPrograms) == 0:
            newItem = GuideItem('[No data]')
            if wrappedI == self.selectedChannel:
               newItem.select()
            layout.addWidget(newItem, 100)
         
         if wrappedI == self.selectedChannel:
            print
         for j in selectedPrograms:
            start = j.starttime
            if start < self.startTime:
               start = self.startTime
            end = j.endtime
            if end > self.startTime + self.displayLength:
               end = self.startTime + self.displayLength
            duration = end - start
            newItem = GuideItem(program = j)
            if wrappedI == self.selectedChannel:
               print start, self.selectedStartTime, end
            if wrappedI == self.selectedChannel and start <= self.selectedStartTime and end > self.selectedStartTime:
               self.select(newItem)
               self.selectedStartTime = start
            layout.addWidget(newItem, int(duration.total_seconds() / self.displayLength.total_seconds() * 100))
            
         
   def select(self, item):
      item.select()
      self.selectedItem = item
      self.programTitle.setText(item.program.title)
      self.programSubtitle.setText(item.program.subtitle)
      self.programDescription.setText(item.program.description)
               
            
            
class GuideItem(QLabel):
   selected = pyqtSignal()
   def __init__(self, text = '', program = None):
      if program != None:
         text = program.title
      QLabel.__init__(self, text)
      
      self.program = program
      
      self.selectedStyle = 'QLabel {border: 3px solid white; font-size: 30pt}'
      self.normalStyle = 'QLabel {border: 1px dashed white; font-size: 30pt}'
      self.setStyleSheet(self.normalStyle)
      self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
      self.setWordWrap(True)
      
      
   def select(self):
      self.setStyleSheet(self.selectedStyle)
   
   def deselect(self):
      self.setStyleSheet(self.normalStyle)