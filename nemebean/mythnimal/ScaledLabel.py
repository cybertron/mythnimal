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
from PyQt4.QtGui import QLabel

fullScale = 1

class ScaledLabel(QLabel):
   formHeight = 0
   def __init__(self, text = '', parent = None, scale = fullScale):
      super(ScaledLabel, self).__init__(text, parent)
      
      self.scale = scale
      self.scaledHeight = self.calcHeight()
      self.setStyle('')
      
   def resizeEvent(self, event):
      oldHeight = self.scaledHeight
      self.scaledHeight = self.calcHeight()
      # It can be slow to setStyle on every resizeEvent
      if oldHeight != self.scaledHeight:
         self.setMinimumHeight(self.scaledHeight * 1.1)
         self.setStyle(self.extraStyle)
      
   def calcHeight(self):
      # .03 seems to be a good default
      retval = self.formHeight * .03 * (self.scale / fullScale)
      return int(retval) if retval > 0 else 20
      
      
   def setStyle(self, style):
      self.extraStyle = style
      fullStyle = 'QLabel {font-size: %dpx; %s}' % (self.scaledHeight, self.extraStyle)
      super(ScaledLabel, self).setStyleSheet(fullStyle)
      
      
   def setStyleSheet(self, dummy):
      raise Exception("Use setStyle instead of this function.")
      