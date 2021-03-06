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
from PyQt5.QtWidgets import *

class PairWidget(QWidget):
   def __init__(self, label, widget, parent = None):
      QWidget.__init__(self, parent)
      
      self.layout = QHBoxLayout(self)
      self.layout.setContentsMargins(0, 0, 0, 0)
      
      self.label = label
      try:
         self.layout.addWidget(self.label)
      except:
         self.label = QLabel(label)
         self.layout.addWidget(self.label)
      
      self.widget = widget
      self.layout.addWidget(self.widget)