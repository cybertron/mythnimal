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
from PyQt4.QtGui import *
from PyQt4.QtCore import Qt, pyqtSignal, QTimer
from Settings import settings
from Player import Player
from MythDB import MythDB
from MythDBObjects import Program
from MenuWidget import MenuWidget
from MenuItem import SimpleMenuItem, ProgramMenuItem
from TabWidget import TabWidget
from PairWidget import PairWidget
from MythControl import MythControl
from ScaledLabel import ScaledLabel
import os
import time

class MainForm(QDialog):
   mythControl = None
   def __init__(self, parent = None):
      QDialog.__init__(self, parent)
      self.previousChannel = None
      
      self.setupUI()
      
      if settings['firstRun']:
         self.initialSetup()
      
      self.mythDB = MythDB(settings['dbHost'], settings['dbUser'], settings['dbPassword'])
      self.mythControl = MythControl(self.mythDB)
      self.refreshShowList()
      
      self.setWindowTitle('Mythnimal')
      self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowMinMaxButtonsHint)
      self.resize(1024, 600)
      self.mainMenu.focus()
      self.show()
      
      
   def setupUI(self):
      self.tabLayout = QVBoxLayout(self)
      self.tabs = TabWidget()
      self.tabLayout.addWidget(self.tabs)
      self.mainMenuTab = self.tabs.createTab('Main Menu')
      self.mainMenuLayout = QVBoxLayout(self.mainMenuTab)
      
      self.mainMenu = MenuWidget()
      self.mainMenu.selected.connect(self.mainMenuSelected)
      self.mainMenu.exit.connect(self.close)
      self.mainMenu.add(SimpleMenuItem('Live TV'))
      self.mainMenu.add(SimpleMenuItem('Watch Recordings'))
      self.mainMenu.add(SimpleMenuItem('Settings'))
      self.mainMenuLayout.addWidget(self.mainMenu)
      
      self.createRecordingsTab()
      self.createSettingsTab()
      
      self.messageDialog = MessageDialog(self)

      
   def createRecordingsTab(self):
      self.recordingsTab = self.tabs.createTab('Recordings')
      self.columnLayout = QHBoxLayout(self.recordingsTab)
      
      self.showMenu = MenuWidget()
      self.showMenu.selected.connect(self.showSelected)
      self.showMenu.exit.connect(self.exitShowMenu)
      self.showMenu.selectionChanged.connect(self.filterByShow)
      self.columnLayout.addWidget(self.showMenu, 1)
      
      self.programMenu = MenuWidget()
      self.programMenu.selected.connect(self.programSelected)
      self.programMenu.exit.connect(self.exitProgramMenu)
      self.programMenu.selectionChanged.connect(self.displayProgramDetails)
      self.columnLayout.addWidget(self.programMenu, 1)
      
      self.programInfoLayout = QVBoxLayout()
      self.programThumbnail = self.wrappedLabel()
      self.programInfoLayout.addWidget(self.programThumbnail)
      
      self.programChannel = self.wrappedLabel()
      self.programInfoLayout.addWidget(self.programChannel)
      self.programTitle = self.wrappedLabel()
      self.programInfoLayout.addWidget(self.programTitle)
      self.programSubtitle = self.wrappedLabel()
      self.programInfoLayout.addWidget(self.programSubtitle)
      self.programStartTime = self.wrappedLabel()
      self.programInfoLayout.addWidget(self.programStartTime)
      self.programTime = self.wrappedLabel()
      self.programInfoLayout.addWidget(self.programTime)
      self.programDescription = self.wrappedLabel()
      self.programInfoLayout.addWidget(self.programDescription, 1)
      
      self.columnLayout.addLayout(self.programInfoLayout, 1)
      
      
   def createSettingsTab(self):
      self.settingsTab = self.tabs.createTab('Settings')
      
      self.settingsLayout = QVBoxLayout(self.settingsTab)
      
      self.settingsInputLayout = QHBoxLayout()
      self.settingsLayout.addLayout(self.settingsInputLayout)
      
      self.dbGroup = QGroupBox('DB/Filesystem')
      self.dbGroupLayout = QVBoxLayout()
      self.dbGroup.setLayout(self.dbGroupLayout)
      self.settingsInputLayout.addWidget(self.dbGroup)
      
      self.dbHostInput = QLineEdit()
      self.dbGroupLayout.addWidget(PairWidget('DB Hostname', self.dbHostInput))
      self.dbUserInput = QLineEdit()
      self.dbGroupLayout.addWidget(PairWidget('DB Username', self.dbUserInput))
      self.dbPasswordInput = QLineEdit()
      self.dbGroupLayout.addWidget(PairWidget('DB Password', self.dbPasswordInput))
      self.fileDirInput = QLineEdit()
      self.dbGroupLayout.addWidget(PairWidget('Local Myth File Directory', self.fileDirInput))
      
      self.miscGroup = QGroupBox('Miscellaneous')
      self.miscGroupLayout = QVBoxLayout()
      self.miscGroup.setLayout(self.miscGroupLayout)
      self.settingsInputLayout.addWidget(self.miscGroup)
      
      self.mplayerInput = QLineEdit()
      self.miscGroupLayout.addWidget(PairWidget('MPlayer Command', self.mplayerInput))
      
      self.bufferTimeInput = QSpinBox()
      self.miscGroupLayout.addWidget(PairWidget('Buffer Time', self.bufferTimeInput))
      
      self.settingsButtonLayout = QHBoxLayout()
      self.settingsLayout.addLayout(self.settingsButtonLayout)
      
      self.saveSettingsButton = QPushButton('Save')
      self.saveSettingsButton.clicked.connect(self.saveSettings)
      self.settingsButtonLayout.addWidget(self.saveSettingsButton)
      
      self.discardSettingsButton = QPushButton('Discard')
      self.discardSettingsButton.clicked.connect(self.discardSettings)
      self.settingsButtonLayout.addWidget(self.discardSettingsButton)
      
      
   def wrappedLabel(self):
      label = ScaledLabel()
      label.setWordWrap(True)
      return label
      
      
   def refreshShowList(self):
      self.showMenu.reset()
      newItem = SimpleMenuItem('[All]')
      newItem.id = '%'
      self.showMenu.add(newItem)
      self.showFilter = '%'
      shows = self.mythDB.showList()
      for i in shows:
         self.showMenu.add(SimpleMenuItem(i.title))
         
      self.refreshProgramList()
         
   def refreshProgramList(self):
      self.programMenu.reset()
      programs = self.mythDB.programList(self.showFilter)
      for i in programs:
         self.programMenu.add(ProgramMenuItem(i))
         
         
   def filterByShow(self, index):
      item = self.showMenu.selectedItem()
      self.showFilter = item.id
      self.refreshProgramList()
         
         
   def showSelected(self):
      self.programMenu.focus()
      self.displayProgramDetails()
      
   def exitProgramMenu(self):
      self.showMenu.focus()
      
      
   def exitShowMenu(self):
      self.tabs.setCurrentWidget(self.mainMenuTab)
      
      
   def displayProgramDetails(self):
      selected = self.programMenu.selectedItem()
      if selected is None:
         return
      details = self.mythDB.getProgram(selected.id)
      if details is None:
         self.refreshProgramList()
         return
      channel = self.mythDB.getChannel(details.chanid)
      filename = self.getFullPath(details.basename)
      filename += '.png'
      self.programThumbnail.setPixmap(QPixmap(filename))
      if channel is not None:
         self.programChannel.setText(channel.channum + ' ' + channel.name)
      else:
         self.programChannel.setText('NA')
      self.programTitle.setText(details.title)
      self.programSubtitle.setText(details.subtitle)
      startTime = self.mythDB.fromUTC(details.starttime).strftime('%Y-%M-%d %I:%M %p')
      self.programStartTime.setText(startTime)
      self.programTime.setText(str(int((details.endtime - details.starttime).total_seconds() / 60)) + ' minutes')
      self.programDescription.setText(details.description)
      
      
   # Index is ignored
   def programSelected(self, index):
      self.startPlayer(self.programMenu.selectedItem().id, live = False)
      
      
   # TODO Needs to be reimplemented using MenuItem signals
   def mainMenuSelected(self, index):
      if index == 0:
         self.startLiveTV()
      elif index == 1:
         self.refreshShowList()
         self.tabs.setCurrentWidget(self.recordingsTab)
      elif index == 2:
         self.showSettingsTab()
      else:
         print 'Unimplemented main menu item selected'
         
         
   def populateSettings(self):
      self.dbHostInput.setText(settings['dbHost'])
      self.dbUserInput.setText(settings['dbUser'])
      self.dbPasswordInput.setText(settings['dbPassword'])
      self.fileDirInput.setText(settings['mythFileDir'])
      self.mplayerInput.setText(settings['mplayer'])
      self.bufferTimeInput.setValue(settings['bufferTime'])
      
   def showSettingsTab(self):
      self.populateSettings()
      self.tabs.setCurrentWidget(self.settingsTab)
   
   
   def saveSettings(self):
      settings['dbHost'] = str(self.dbHostInput.text())
      settings['dbUser'] = str(self.dbUserInput.text())
      settings['dbPassword'] = str(self.dbPasswordInput.text())
      settings['mythFileDir'] = str(self.fileDirInput.text())
      settings['mplayer'] = str(self.mplayerInput.text())
      settings['bufferTime'] = self.bufferTimeInput.value()
      settings.save()
      if settings['firstRun']:
         self.initConfig.hide()
      self.tabs.setCurrentWidget(self.mainMenuTab)
   
   def discardSettings(self):
      self.tabs.setCurrentWidget(self.mainMenuTab)
      
      
   def closeEvent(self, event):
      settings.save()
      
      
   def resizeEvent(self, event):
      ScaledLabel.formHeight = event.size().height()
      
      
   def initialSetup(self):
      self.initConfig = QDialog()
      self.initConfig.setLayout(self.settingsLayout)
      self.populateSettings()
      self.initConfig.exec_()
      self.settingsTab.setLayout(self.settingsLayout)
      settings['firstRun'] = False
      
      
   def startLiveTV(self):
      self.messageDialog.showMessage('Buffering...')
      filename = self.mythControl.startLiveTV(qApp.processEvents)
      self.messageDialog.hide()
      self.startPlayer(filename, live = True)
      
         
   def changeChannel(self, channel):
      self.messageDialog.showMessage('Buffering...')
      self.previousChannel = self.mythControl.currentChannel
      filename = self.mythControl.changeChannel(channel, qApp.processEvents)
      # This is highly unlikely, but possible
      if filename is None:
         self.messageDialog.showMessageTimed('Channel change failed')
      self.messageDialog.hide()
      self.startPlayer(filename, live = True)
      
      
   def startPlayer(self, filename, live = False, startAtEnd = False):
      if filename is not None:
         playerX = self.x() + self.width() / 2
         playerY = self.y() + self.height() / 2
         self.player = Player(playerX, playerY, filename, self.mythDB, startAtEnd)
         self.player.finished.connect(self.activateWindow)
         if live:
            if self.previousChannel is None:
               self.previousChannel = self.mythControl.currentChannel
            self.player.previousChannel = self.previousChannel
            self.player.finished.connect(self.playerStopped)
            self.player.channelChange.connect(self.changeChannel)
            self.player.seekedPastStart.connect(self.playPreviousInChain)
            self.player.toggleRecording.connect(self.toggleRecording)
            self.player.currentChannel = self.mythControl.currentChannel
            
            
   def playerStopped(self, eof):
      if not eof:
         self.mythControl.stopLiveTV()
         self.activateWindow()
      else: # Go to the next live TV recording
         nextChain = None
         while nextChain == None:
            i, chain, currentChain = self.getCurrentChain()
            if i + 1 < len(chain):
               nextChain = chain[i + 1]
            else:
               print 'Waiting for next program to start'
         nextProgram = self.mythDB.getProgramByChain(nextChain)
         self.player.emitFinished = False
         self.player.end(eof = False)
         self.startPlayer(nextProgram.basename, live = True)
         
         
   def playPreviousInChain(self):
      i, chain, currentChain = self.getCurrentChain()
      if i > 0:
         nextProgram = self.mythDB.getProgramByChain(chain[i - 1])
         self.player.emitFinished = False
         self.player.end(eof = False)
         self.startPlayer(nextProgram.basename, live = True, startAtEnd = True)
   
   
   def getCurrentChain(self):
      currentProgram = self.mythDB.getProgram(self.player.filename)
      chain = self.mythDB.getTVChain(self.mythControl.chain)
      for i, entry in enumerate(chain):
         if entry.chanid == currentProgram.chanid and entry.starttime == currentProgram.starttime:
            return i, chain, entry
            
            
   def toggleRecording(self):
      program = self.mythDB.getProgram(self.player.filename)
      self.mythControl.toggleRecording(program)
      if self.mythControl.recordCurrent:
         self.player.showMessage('Recording current program')
      else:
         self.player.showMessage('Not recording current program')
      
            
   def keyPressEvent(self, event):
      key = event.key()
      if self.programMenu.hasFocus():
         if key == Qt.Key_M:
            self.showProgramMenu()
         
         
   def showProgramMenu(self):
      self.menuDialog = QDialog(self)
      menuLayout = QVBoxLayout(self.menuDialog)
      
      selected = self.mythDB.getProgram(self.programMenu.selectedItem().id)
      title = ScaledLabel(selected.title)
      menuLayout.addWidget(title)
      subtitle = ScaledLabel(selected.subtitle)
      menuLayout.addWidget(subtitle)
      
      programOptions = MenuWidget(self)
      programOptions.exit.connect(self.menuDialog.close)
      menuLayout.addWidget(programOptions)
      
      item = SimpleMenuItem('Delete')
      item.selected.connect(self.deleteSelected)
      programOptions.add(item)
      item = SimpleMenuItem('Delete and re-record')
      item.selected.connect(self.deleteAndRerecord)
      programOptions.add(item)
      
      self.menuDialog.exec_()
      self.menuDialog = None # For some reason not doing this results in segfaults
      
   def deleteSelected(self):
      self.deleteSelectedProgram(False)
      self.menuDialog.close()
   
   def deleteAndRerecord(self):
      self.deleteSelectedProgram(True)
      self.menuDialog.close()
      
      
   def deleteSelectedProgram(self, rerecord):
      selected = self.programMenu.selectedItem()
      selectedProgram = self.mythDB.getProgram(selected.id)
      self.mythControl.deleteProgram(selectedProgram, rerecord)
      self.programMenu.remove(selected)
      
      
   def getFullPath(self, basename):
      return os.path.join(settings['mythFileDir'], basename)
      
      
class MessageDialog(QDialog):
   def __init__(self, parent = None):
      QDialog.__init__(self, parent)
      self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
      self.layout = QVBoxLayout(self)
      self.label = ScaledLabel()
      self.label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
      self.layout.addWidget(self.label)
      
      self.timer = QTimer()
      self.timer.timeout.connect(self.hide)
      self.timer.setSingleShot(True)
      
      
   def showMessage(self, message):
      self.label.setText(message)
      self.show()
      self.raise_()
      
      
   def showMessageTimed(self, message, timeout = 3000):
      self.showMessage(message)
      self.timer.start(timeout)
      
      