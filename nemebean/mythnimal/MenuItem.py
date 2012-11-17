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
# Copyright 2012 Ben Nemec
# @End License@
from PyQt4.QtGui import QWidget, QLabel, QPalette, QColor, QHBoxLayout
from PyQt4.QtCore import Qt, pyqtSignal

class MenuItem(QWidget):
   """Base class for items that can be inserted into a MenuWidget"""
   selected = pyqtSignal()
   def __init__(self):
      QWidget.__init__(self)
      
      self.id = None
      
   def select(self):
      pass
   
   def deselect(self):
      pass
   
   
class SimpleMenuItem(MenuItem):
   def __init__(self, title):
      MenuItem.__init__(self)
      
      self.id = title
      self.layout = QHBoxLayout(self)
      self.label = QLabel(title)
      self.layout.addWidget(self.label)
      
      self.baseStyle = self.label.styleSheet()
      self.selectedStyle = 'QLabel { text-decoration: underline; }'
      self.focusedSelectedStyle = 'QLabel { font-weight: bold; text-decoration: underline; }'
      
      self.setMinimumHeight(25)
      
   def select(self, focus):
      if not focus:
         self.label.setStyleSheet(self.selectedStyle)
      else:
         self.label.setStyleSheet(self.focusedSelectedStyle)
      
   def deselect(self):
      self.label.setStyleSheet(self.baseStyle)
      
   
   
from MythDBObjects import Program

class ProgramMenuItem(MenuItem):
   def __init__(self, programData):
      MenuItem.__init__(self)
      
      self.programData = programData
      self.id = programData.basename
      
      self.layout = QHBoxLayout(self)
      
      text = programData.title
      if programData.subtitle != '':
         text += ' - ' + programData.subtitle
      self.programLabel = QLabel(text)
      self.layout.addWidget(self.programLabel)
      
      self.baseStyle = self.programLabel.styleSheet()
      self.focusedSelectedStyle = 'QLabel { font-weight: bold; text-decoration: underline; }'
      
      self.setMinimumHeight(25)
      
      
   def select(self, focus):
      if not focus:
         self.programLabel.setStyleSheet(self.baseStyle)
      else:
         self.programLabel.setStyleSheet(self.focusedSelectedStyle)
      
   def deselect(self):
      self.programLabel.setStyleSheet(self.baseStyle)