from ConfigHandler import ConfigHandler

class Settings:
   def __init__(self):
      self.values = dict()
      self.values['mythFileDir'] = '/mnt/tv/tv'
      self.values['dbHost'] = 'torch'
      self.values['dbUser'] = 'mythtv'
      self.values['dbPassword'] = 'mythtv'
      self.values['firstRun'] = True
      
      self.configHandler = ConfigHandler('mythnimal')
      self.configHandler.loadDict('settings', self.values)
      
   def __getitem__(self, key):
      return self.values[key]
      
   def __setitem__(self, key, value):
      self.values[key] = value
      
   def save(self):
      self.configHandler.saveObject('settings', self.values)