from PyQt4.QtGui import *
from Settings import Settings
from Player import Player
from MythDB import MythDB, Program
from MenuWidget import MenuWidget
from SimpleMenuItem import SimpleMenuItem
from ProgramMenuItem import ProgramMenuItem
from TabWidget import TabWidget
from PairWidget import PairWidget
from MythControl import MythControl
import os

class MainForm(QDialog):
   settings = Settings()
   mythControl = None
   def __init__(self, parent = None):
      QDialog.__init__(self, parent)
      
      self.setupUI()
      
      if self.settings['firstRun']:
         self.initialSetup()
      
      self.mythDB = MythDB(self.settings['dbHost'], self.settings['dbUser'], self.settings['dbPassword'])
      self.mythControl = MythControl(self.mythDB)
      self.refreshShowList()
      
      self.setWindowTitle('Mythnimal')
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
      self.programDescription = QTextEdit()
      self.programInfoLayout.addWidget(self.programDescription)
      
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
      self.dbGroupLayout.addWidget(PairWidget('Hostname', self.dbHostInput))
      self.dbUserInput = QLineEdit()
      self.dbGroupLayout.addWidget(PairWidget('Username', self.dbUserInput))
      self.dbPasswordInput = QLineEdit()
      self.dbGroupLayout.addWidget(PairWidget('Password', self.dbPasswordInput))
      self.fileDirInput = QLineEdit()
      self.dbGroupLayout.addWidget(PairWidget('Myth File Directory', self.fileDirInput))
      
      
      self.settingsButtonLayout = QHBoxLayout()
      self.settingsLayout.addLayout(self.settingsButtonLayout)
      
      self.saveSettingsButton = QPushButton('Save')
      self.saveSettingsButton.clicked.connect(self.saveSettings)
      self.settingsButtonLayout.addWidget(self.saveSettingsButton)
      
      self.discardSettingsButton = QPushButton('Discard')
      self.discardSettingsButton.clicked.connect(self.discardSettings)
      self.settingsButtonLayout.addWidget(self.discardSettingsButton)
      
      
   def wrappedLabel(self):
      label = QLabel()
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
      details = self.mythDB.getProgram(self.programMenu.selectedItem().id)
      channel = self.mythDB.getChannel(details.chanid)
      filename = os.path.join(self.settings['mythFileDir'], details.basename)
      filename += '.png'
      self.programThumbnail.setPixmap(QPixmap(filename))
      self.programChannel.setText(channel.channum + ' ' + channel.name)
      self.programTitle.setText(details.title)
      self.programSubtitle.setText(details.subtitle)
      self.programDescription.setText(details.description)
      
      
   # Index is ignored
   def programSelected(self, index):
      self.startPlayer(self.programMenu.selectedItem().id, live = False)
      
      
   def mainMenuSelected(self, index):
      if index == 0:
         self.startLiveTV()
      elif index == 1:
         self.tabs.setCurrentWidget(self.recordingsTab)
      elif index == 2:
         self.showSettingsTab()
      else:
         print 'Unimplemented main menu item selected'
         
         
   def showSettingsTab(self):
      self.dbHostInput.setText(self.settings['dbHost'])
      self.dbUserInput.setText(self.settings['dbUser'])
      self.dbPasswordInput.setText(self.settings['dbPassword'])
      self.fileDirInput.setText(self.settings['mythFileDir'])
      self.tabs.setCurrentWidget(self.settingsTab)
   
   
   def saveSettings(self):
      self.settings['dbHost'] = str(self.dbHostInput.text())
      self.settings['dbUser'] = str(self.dbUserInput.text())
      self.settings['dbPassword'] = str(self.dbPasswordInput.text())
      self.settings['mythFileDir'] = str(self.fileDirInput.text())
      self.settings.save()
      self.initConfig.hide()
      self.tabs.setCurrentWidget(self.mainMenuTab)
   
   def discardSettings(self):
      self.tabs.setCurrentWidget(self.mainMenuTab)
      
      
   def closeEvent(self, event):
      self.settings.save()
      
      
   def initialSetup(self):
      self.initConfig = QDialog()
      self.initConfig.setLayout(self.settingsLayout)
      self.initConfig.exec_()
      self.settingsTab.setLayout(self.settingsLayout)
      self.settings['firstRun'] = False
      
      
   def startLiveTV(self):
      filename = self.mythControl.startLiveTV()
      self.startPlayer(filename, live = True)
      
         
   def changeChannel(self, channel):
      filename = self.mythControl.changeChannel(channel)
      self.startPlayer(filename, live = True)
      
      
   def startPlayer(self, filename, live = False):
      if filename is not None:
         self.player = Player(self.x(), self.y(), filename, self.mythDB)
         if live:
            self.player.finished.connect(self.mythControl.stopLiveTV)
            self.player.channelChange.connect(self.changeChannel)
            self.player.currentChannel = self.mythControl.currentChannel
            
      