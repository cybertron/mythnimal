import cPickle, os

class ConfigHandler:
   def __init__(self, appName):
      self.appName = appName
      self.configDir = os.path.expanduser('~/.' + self.appName)
      if not os.path.isdir(self.configDir):
         os.mkdir(self.configDir)
      
      
   def saveObject(self, name, obj):
      filename = os.path.join(self.configDir, name)
      with open(filename, 'wb') as f:
         cPickle.dump(obj, f)
   

   def loadDict(self, name, default):
      retval = default
      filename = os.path.join(self.configDir, name)
      # Don't load directly so we can add new default values as needed
      temp = self.loadConfig(filename, default)
      for key, value in temp.items():
         retval[key] = value
         
      return retval
         
         
   def loadConfig(self, filename, default):
      if os.path.exists(filename):
         with open(filename, 'rb') as f:
            return cPickle.load(f)
      else:
         return default