from PyQt4.QtGui import *
from Settings import Settings
from Player import Player
from MythDB import MythDB
from MenuWidget import MenuWidget
from ShowMenuItem import ShowMenuItem
from ProgramMenuItem import ProgramMenuItem

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
      self.columnLayout.addWidget(self.showMenu)
      
      self.programMenu = MenuWidget()
      self.programMenu.selected.connect(self.programSelected)
      self.programMenu.exit.connect(self.exitProgramMenu)
      self.programMenu.selectionChanged.connect(self.displayProgramDetails)
      self.columnLayout.addWidget(self.programMenu)
      
      self.programInfoLayout = QVBoxLayout()
      self.columnLayout.addLayout(self.programInfoLayout)
      
      
   def initSettings(self):
      pass
      
   def refreshShowList(self):
      self.showMenu.reset()
      newItem = ShowMenuItem('All')
      newItem.id = '%'
      self.showMenu.add(newItem)
      self.showFilter = '%'
      shows = self.mythDB.showList()
      for i in shows:
         self.showMenu.add(ShowMenuItem(i[0]))
         
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
      pass
      
      
   def programSelected(self, index):
      self.player = Player(self.x(), self.y(), self.programMenu.selectedItem().id)
      
      