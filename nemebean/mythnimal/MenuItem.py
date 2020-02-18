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
from PyQt5.QtWidgets import QWidget, QHBoxLayout
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt, pyqtSignal
from ScaledLabel import ScaledLabel

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
      self.label = ScaledLabel(title)
      self.layout.addWidget(self.label)
      
      self.selectedStyle = 'border: 1px dotted white'
      self.focusedSelectedStyle = 'border: 1px solid white'
      self.deselect()
      
   def select(self, focus):
      if not focus:
         self.label.setStyle(self.selectedStyle)
      else:
         self.label.setStyle(self.focusedSelectedStyle)
      
   def deselect(self):
      self.label.setStyle('')
      
   
   
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
      self.programLabel = ScaledLabel(text)
      self.layout.addWidget(self.programLabel)
      
      self.focusedSelectedStyle = 'border: 1px solid white'
      self.deselect()
      
      
   def select(self, focus):
      if not focus:
         self.programLabel.setStyle('')
      else:
         self.programLabel.setStyle(self.focusedSelectedStyle)
      
   def deselect(self):
      self.programLabel.setStyle('')
