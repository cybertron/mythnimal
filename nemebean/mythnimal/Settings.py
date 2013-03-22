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
from ConfigHandler import ConfigHandler

class Settings:
   def __init__(self):
      self.values = dict()
      self.values['mythFileDir'] = '/mnt/tv/tv'
      self.values['dbHost'] = 'torch'
      self.values['dbUser'] = 'mythtv'
      self.values['dbPassword'] = 'mythtv'
      self.values['firstRun'] = True
      self.values['deinterlace'] = True
      self.values['bufferTime'] = 5
      self.values['lengthUpdateInterval'] = 3000
      self.values['mplayer'] = 'mplayer'
      
      self.configHandler = ConfigHandler('mythnimal')
      self.configHandler.loadDict('settings', self.values)
      
   def __getitem__(self, key):
      return self.values[key]
      
   def __setitem__(self, key, value):
      self.values[key] = value
      
   def save(self):
      self.configHandler.saveObject('settings', self.values)
      

settings = Settings()