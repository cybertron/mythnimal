from PyQt4.QtGui import *
from Settings import Settings
from Player import Player
from MythDB import MythDB, Program
from MenuWidget import MenuWidget
from ShowMenuItem import ShowMenuItem
from ProgramMenuItem import ProgramMenuItem
import os

class MainForm(QDialog):
   settings = Settings()
   def __init__(self, parent = None):
      QDialog.__init__(self, parent)
      
      self.initSettings()
      
      self.setupUI()
      
      self.mythDB = MythDB('torch', 'mythtv', 'mythtv')
      self.refreshShowList()
      
      self.setWindowTitle('Mythnimal')
      self.resize(1024, 600)
      self.show()
      
      
   def setupUI(self):
      self.columnLayout = QHBoxLayout(self)
      
      self.showMenu = MenuWidget()
      self.showMenu.selected.connect(self.showSelected)
      self.showMenu.exit.connect(self.close)
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
      
      
   def wrappedLabel(self):
      label = QLabel()
      label.setWordWrap(True)
      return label
      
      
   def initSettings(self):
      pass
      
   def refreshShowList(self):
      self.showMenu.reset()
      newItem = ShowMenuItem('[All]')
      newItem.id = '%'
      self.showMenu.add(newItem)
      self.showFilter = '%'
      shows = self.mythDB.showList()
      for i in shows:
         self.showMenu.add(ShowMenuItem(i.title))
         
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
      
      
   def exitProgramMenu(self):
      self.showMenu.focus()
      
      
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
      
      
   def programSelected(self, index):
      self.player = Player(self.x(), self.y(), self.programMenu.selectedItem().id, self.mythDB)
      
      