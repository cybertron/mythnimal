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
import pickle, os

class ConfigHandler:
   def __init__(self, appName):
      self.appName = appName
      self.configDir = os.path.expanduser('~/.' + self.appName)
      if not os.path.isdir(self.configDir):
         os.mkdir(self.configDir)
      
      
   def saveObject(self, name, obj):
      filename = os.path.join(self.configDir, name)
      with open(filename, 'wb') as f:
         pickle.dump(obj, f)
   

   def loadDict(self, name, default):
      retval = default
      filename = os.path.join(self.configDir, name)
      # Don't load directly so we can add new default values as needed
      temp = self.loadConfig(filename, default)
      for key, value in list(temp.items()):
         retval[key] = value
         
      return retval
         
         
   def loadConfig(self, filename, default):
      if os.path.exists(filename):
         with open(filename, 'rb') as f:
            return pickle.load(f)
      else:
         return default