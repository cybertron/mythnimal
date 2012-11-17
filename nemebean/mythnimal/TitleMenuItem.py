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
from MenuItem import MenuItem
from PyQt4.QtGui import QLabel, QPalette, QColor
from PyQt4.QtCore import Qt

class ShowMenuItem(MenuItem):
   def __init__(self, title):
      MenuItem.__init__(self)
      
      self.id = title
      self.label = QLabel(title, self)
      self.baseStyle = self.label.styleSheet()
      self.selectedStyle = 'QLabel { background-color: blue; }'
      
      self.setMinimumHeight(25)
      
   def select(self):
      self.label.setStyleSheet(self.selectedStyle)
      
   def deselect(self):
      self.label.setStyleSheet(self.baseStyle)
      