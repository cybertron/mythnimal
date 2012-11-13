import socket

class Version:
   def __init__(self, num, token):
      self.num = num
      self.token = token

class MythControl:
   supportedVersions = [Version(63, '3875641D')]
   def __init__(self, mythDB):
      self.mythDB = mythDB
      self.connected = False
      
      self.backendIP = self.mythDB.getSetting('MasterServerIP')
      self.backendPort = int(self.mythDB.getSetting('MasterServerPort'))
      self.backendVersion = None
      
      self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.socket.connect((self.backendIP, self.backendPort))
      
      self.negotiateVersion()
      self.annPlayback()
      
      
   def __del__(self):
      self.sendCommand('DONE')
      
      
   def sendCommand(self, command, response=False):
      length = len(command)
      length = str(length).ljust(8)
      commandStr = length + command
      print 'Sending:', commandStr
      self.socket.sendall(commandStr)
      if response:
         length = self.socket.recv(8)
         data = self.socket.recv(int(length))
         return data
      return None
      
      
   def negotiateVersion(self):
      response = ''
      for nextVersion in self.supportedVersions:
         response = self.sendCommand('MYTH_PROTO_VERSION ' + str(nextVersion.num) + ' ' + nextVersion.token, response=True)
         if response.startswith('ACCEPT'):
            self.connected = True
            break
      
      
   def annPlayback(self):
      response = self.sendCommand('ANN Playback ' + socket.gethostname() + ' 0', response=True)
      if not response.startswith('OK'):
         self.connected = False