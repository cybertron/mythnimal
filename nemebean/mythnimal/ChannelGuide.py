# @Begin License@
# This file is part of Mythnimal.
#
# Mythnimal is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mythnimal is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mythnimal.  If not, see <http:#www.gnu.org/licenses/>.
#
# Copyright 2012, 2013 Ben Nemec
# @End License@
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QWidget, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal
import datetime
from ScaledLabel import ScaledLabel

class ChannelGuide(QDialog):
   channelSelected = pyqtSignal(str)
   def __init__(self, startChannel, mythDB, videoWidget, parent = None):
      QDialog.__init__(self, parent)
      self.mythDB = mythDB
      self.videoWidget = videoWidget
      self.visibleChannels = 11
      self.startTime = datetime.datetime.today()
      if self.mythDB.isUTC():
         self.startTime = datetime.datetime.utcnow()
      self.startTime.replace(second = 0, microsecond = 0)
      if self.startTime.minute >= 30:
         self.startTime = self.startTime.replace(minute = 30)
      else:
         self.startTime = self.startTime.replace(minute = 0)
      self.selectedStartTime = self.startTime
      self.displayLength = datetime.timedelta(hours = 2)
      self.displayResolution = datetime.timedelta(minutes = 30)
      self.itemCache = {}
      self.lineLayouts = []
      
      self.channels = self.mythDB.getAllChannels()
      self.channels = sorted(self.channels, key = lambda x: x.chanid)
      
      chan = [i for i in self.channels if i.channum == startChannel][0]
      self.selectedChannel = self.channels.index(chan)
      
      self.setupUI()
      
      self.refreshDisplay()
      
      
   def setupUI(self):
      self.setStyleSheet('QDialog { background-color: black; }')
      self.mainLayout = QHBoxLayout(self)
      
      self.channelWidget = QWidget()
      self.mainLayout.addWidget(self.channelWidget, 3)
      self.channelLayout = QHBoxLayout(self.channelWidget)
      
      self.infoLayout = QVBoxLayout()
      self.mainLayout.addLayout(self.infoLayout, 1)
      
      self.infoLayout.addWidget(self.videoWidget, 3)
      self.programTitle = self.createLabel('Title')
      self.infoLayout.addWidget(self.programTitle, 1)
      self.programSubtitle = self.createLabel('Subtitle')
      self.infoLayout.addWidget(self.programSubtitle, 1)
      self.programDescription = self.createLabel('Description')
      self.infoLayout.addWidget(self.programDescription, 5)
      
   def createLabel(self, text):
      label = ScaledLabel(text)
      label.setWordWrap(True)
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
      elif key == Qt.Key_PageUp:
         self.selectedChannel -= self.visibleChannels / 2
         self.validateSelected()
         self.refreshDisplay()
      elif key == Qt.Key_PageDown:
         self.selectedChannel += self.visibleChannels / 2
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
         
         
   def hideEvent(self, event):
      self.videoWidget.setParent(None)
      self.videoWidget.showFullScreen()
         
         
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
      
      # setVisible is surprisingly slow, so don't do it unnecessarily
      self.needToHide = set()
      # A widget is owned by its parent layout, so if we don't remove them from the layout
      # first they will all be deleted, which breaks our caching
      for i in self.lineLayouts:
         while i.count():
            self.needToHide.add(i.takeAt(0).widget())
      self.lineLayouts = []
      QWidget().setLayout(self.channelLayout)
      self.channelLayout = QVBoxLayout(self.channelWidget)
      
      def newGuideLine(text):
         layout = QHBoxLayout()
         
         def callback(newItem):
            newItem.setMaximumWidth(125)
            newItem.setMinimumWidth(125)
            newItem.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Ignored)
            newItem.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
         newItem = self.getItem(text = text, callback = callback)
         
         layout.addWidget(newItem)
         self.lineLayouts.append(layout)
         
         return layout
         
      layout = newGuideLine('')
      self.channelLayout.addLayout(layout)
      currTime = self.startTime
      while currTime < self.startTime + self.displayLength:
         timeText = self.mythDB.fromUTC(currTime).time().strftime('%I:%M %p')
         callback = lambda x: x.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
         newItem = self.getItem(text = timeText, callback = callback)
         layout.addWidget(newItem)
         currTime += self.displayResolution
      
      # Don't use rawI directly
      for rawI in range(startChanIndex, endChanIndex):
         wrappedI = rawI % len(self.channels)
         channel = self.channels[wrappedI]
         chanId = channel.chanid
         
         selectedPrograms = self.mythDB.getProgramSchedule(self.startTime,
                                                           self.startTime + self.displayLength,
                                                           chanId)
         
         def sortByStarttime(i):
            return i.starttime
         selectedPrograms = sorted(selectedPrograms, key = sortByStarttime)
         
         text = str(channel.channum) + '\n' + channel.name
         layout = newGuideLine(text)
         self.channelLayout.addLayout(layout)
         
         if len(selectedPrograms) == 0:
            newItem = self.getItem(text = '[No data]')
            if wrappedI == self.selectedChannel:
               newItem.select()
            layout.addWidget(newItem, 100)
         
         for j in selectedPrograms:
            start = j.starttime
            if start < self.startTime:
               start = self.startTime
            end = j.endtime
            if end > self.startTime + self.displayLength:
               end = self.startTime + self.displayLength
            duration = end - start
            newItem = self.getItem(program = j)
            newItem.deselect()
            if wrappedI == self.selectedChannel and start <= self.selectedStartTime and end > self.selectedStartTime:
               self.select(newItem)
               self.selectedStartTime = start
            layout.addWidget(newItem, int(duration.total_seconds() / self.displayLength.total_seconds() * 100))
            
      for i in self.needToHide:
         i.setVisible(False)
            
         
   def select(self, item):
      item.select()
      self.selectedItem = item
      self.programTitle.setText(item.program.title)
      self.programSubtitle.setText(item.program.subtitle)
      self.programDescription.setText(item.program.description)
      
      
   def getItem(self, text = None, program = None, callback = lambda x: None):
      def doReturn(retval):
         # This may unnecessarily call setVisible on a second retrieval of an item, but
         # that won't happen often so it's good enough.
         if retval not in self.needToHide:
            retval.setVisible(True)
         self.needToHide.discard(retval)
         return retval
         
      if program is not None:
         if program in self.itemCache:
            return doReturn(self.itemCache[program])
         newItem = GuideItem(program = program)
         callback(newItem)
         self.itemCache[program] = newItem
      elif text is not None:
         if text in self.itemCache:
            return doReturn(self.itemCache[text])
         newItem = GuideItem(text = text)
         callback(newItem)
         self.itemCache[text] = newItem
      else:
         raise Exception('Neither text nor program passed to getItem')
      return newItem
               
            
            
class GuideItem(ScaledLabel):
   selected = pyqtSignal()
   def __init__(self, text = '', program = None):
      if program != None:
         text = program.title
      ScaledLabel.__init__(self, text)
      
      self.program = program
      
      self.selectedStyle = 'border: 3px solid white'
      self.normalStyle = 'border: 1px dashed white'
      self.setStyle(self.normalStyle)
      self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
      self.setWordWrap(True)
      
      
   def select(self):
      self.setStyle(self.selectedStyle)
   
   def deselect(self):
      self.setStyle(self.normalStyle)