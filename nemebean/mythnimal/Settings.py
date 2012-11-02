class Settings:
   def __init__(self):
      self.values = dict()
      self.values['mythFileDir'] = '/mnt/tv/tv'
      
   def __getitem__(self, key):
      return self.values[key]
      
   def __setitem__(self, key, value):
      self.values[key] = value