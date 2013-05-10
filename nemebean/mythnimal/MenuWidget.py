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
from PyQt4.QtCore import pyqtSignal, Qt
from PyQt4.QtGui import QWidget, QScrollArea, QVBoxLayout, QLayout

class MenuWidget(QScrollArea):
   selected = pyqtSignal(int)
   exit = pyqtSignal()
   selectionChanged = pyqtSignal(int)
   def __init__(self, parent = None):
      QWidget.__init__(self, parent)
      
      self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
      
      self.reset()
      
      
   def reset(self):
      self.widget = QWidget()
      self.setWidgetResizable(True)
      self.setWidget(self.widget)
      
      self.layout = QVBoxLayout(self.widget)
      self.layout.setSizeConstraint(QLayout.SetMinimumSize)
      self.layout.setSpacing(0)
      self.layout.setContentsMargins(0, 0, 0, 0)
      
      self.items = []
      self.selectedIndex = None
      
      
   def add(self, item):
      # Subtract 20 to account for scroll bar.  I think that's the problem anyway.
      item.setMaximumWidth(self.width() - 20)
      self.layout.addWidget(item)
      self.items.append(item)
      if self.selectedIndex is None:
         self.selectedIndex = 0
         self.updateSelected()
         
         
   def __getitem__(self, index):
      return self.items[index]
      
      
   def remove(self, item):
      self.layout.removeWidget(item)
      self.items = [i for i in self.items if i is not item]
      if len(self.items) == 0:
         self.selectedIndex = None
      else:
         if self.selectedIndex >= len(self.items):
            self.selectedIndex = len(self.items) - 1
         self.selectionChanged.emit(self.selectedIndex)
      item.setParent(None) # Should remove the last reference and trigger deletion
      
      
   def resizeEvent(self, event):
      for i in self.items:
         i.setMaximumWidth(event.size().width())
      
      
   def keyPressEvent(self, event):
      key = event.key()
      changed = False
      if key == Qt.Key_Enter or key == Qt.Key_Return or key == Qt.Key_Right:
         self.selected.emit(self.selectedIndex)
         self.items[self.selectedIndex].selected.emit()
      if key == Qt.Key_Escape or key == Qt.Key_Left:
         self.exit.emit()
      elif key == Qt.Key_Down:
         self.selectedIndex += 1
         changed = True
      elif key == Qt.Key_Up:
         self.selectedIndex -= 1
         changed = True
      else:
         QWidget.keyPressEvent(self, event)
         
      self.validateSelected()
      if changed:
         self.selectionChanged.emit(self.selectedIndex)
         
         
   def validateSelected(self):
      if self.selectedIndex is None:
         return
      if self.selectedIndex >= len(self.items):
         self.selectedIndex = 0
      if self.selectedIndex < 0:
         self.selectedIndex = len(self.items) - 1
         
      self.updateSelected()
      
      
   def updateSelected(self):
      for i in self.items:
         i.deselect()
         
      if self.selectedIndex is not None:
         selectedItem = self.selectedItem()
         selectedItem.select(self.hasFocus())
         self.ensureWidgetVisible(selectedItem)
         
         
   def selectedItem(self):
      if self.selectedIndex is None:
         return None
      return self.items[self.selectedIndex]
      
      
   def focus(self):
      self.setFocus()
      self.updateSelected()
      
      
   def focusInEvent(self, event):
      self.updateSelected()