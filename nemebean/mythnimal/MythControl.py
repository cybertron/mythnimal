import socket, datetime, os
import time

class Version:
   def __init__(self, num, token):
      self.num = num
      self.token = token

class MythControl:
   supportedVersions = [Version(63, '3875641D')]
   def __init__(self, mythDB):
      self.mythDB = mythDB
      self.connected = False
      self.liveTVRecorder = None
      
      self.backendIP = self.mythDB.getSetting('MasterServerIP')
      self.backendPort = int(self.mythDB.getSetting('MasterServerPort'))
      self.backendVersion = None
      
      self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.socket.connect((self.backendIP, self.backendPort))
      
      self.negotiateVersion()
      self.annPlayback()
      
      
   def __del__(self):
      self.sendCommand('DONE', response = False)
      
      
   def sendCommand(self, command, response = True):
      length = len(command)
      length = str(length).ljust(8)
      commandStr = length + command
      print 'Sending:', commandStr
      self.socket.sendall(commandStr)
      if response:
         length = self.socket.recv(8)
         data = self.socket.recv(int(length))
         print data
         return data
      return None
      
      
   def negotiateVersion(self):
      response = ''
      for nextVersion in self.supportedVersions:
         response = self.sendCommand('MYTH_PROTO_VERSION ' + str(nextVersion.num) + ' ' + nextVersion.token)
         if response.startswith('ACCEPT'):
            self.connected = True
            break
      
      
   def annPlayback(self):
      response = self.sendCommand('ANN Playback ' + socket.gethostname() + ' 0')
      if not response.startswith('OK'):
         self.connected = False
         
         
   def startLiveTV(self):
      response = self.sendCommand('GET_NEXT_FREE_RECORDER[]:[]-1')
      parts = response.split('[]:[]')
      self.liveTVRecorder = parts[0]
      if int(self.liveTVRecorder) < 0:
         self.liveTVRecorder = None
         return None
         
      # TODO Check that recorder is not slave backend - that is not supported
         
      args = '[]:[]SPAWN_LIVETV[]:[]live-' + socket.gethostname() + '-' + datetime.datetime.today().isoformat()
      args += '[]:[]0[]:[]3'
      response = self.sendCommand(self.query() + args)
      if not response.startswith('ok'):
         print 'Failed to start live tv'
         self.stopLiveTV()
         return None
         
      if self.waitForRecording():
         # For some reason Myth returns a wrong filename if we do the next step immediately
         # Fortunately, we should wait a few seconds to let it get ahead anyway
         time.sleep(5)
         response = self.sendCommand(self.query() + '[]:[]GET_CURRENT_RECORDING')
         parts = response.split('[]:[]')
         return os.path.basename(parts[8])
      else:
         return None
      
      
   def waitForRecording(self):
      response = ''
      start = datetime.datetime.today()
      while not response.startswith('1'):
         if datetime.datetime.today() - start > datetime.timedelta(seconds = 30):
            print 'Timed out waiting for recording to start'
            self.stopLiveTV()
            return False
         response = self.sendCommand(self.query() + '[]:[]IS_RECORDING')
      return True
      
   
   
   def stopLiveTV(self):
      if self.liveTVRecorder is None:
         return
         
      response = self.sendCommand(self.query() + '[]:[]STOP_LIVETV')
      if not response.startswith('ok'):
         print 'Failed to stop live tv'
         
      response = self.sendCommand(self.query() + '[]:[]FINISH_RECORDING')
      if not response.startswith('ok'):
         print 'Failed to stop recorder'
      
      
   def query(self):
      return 'QUERY_RECORDER ' + self.liveTVRecorder