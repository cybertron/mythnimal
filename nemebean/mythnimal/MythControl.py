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
# Copyright 2012 Ben Nemec
# @End License@
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
      self.currentChannel = None
      self.verbose = True
      
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
      commandStr = str(length + command)
      if self.verbose:
         print 'Sending:', commandStr
      self.socket.sendall(commandStr)
      if response:
         length = self.recv(8)
         data = self.recv(int(length))
         if self.verbose:
            print data
         return data
      return None
      
      
   def recv(self, length):
      done = False
      while not done:
         try:
            data = self.socket.recv(length)
            done = True
         except socket.error as (errno, msg):
            if errno != 4:
               raise
      return data
      
      
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
         
         
   def startLiveTV(self, callback = None):
      response = self.sendCommand('GET_NEXT_FREE_RECORDER[]:[]-1')
      parts = response.split('[]:[]')
      self.liveTVRecorder = parts[0]
      if int(self.liveTVRecorder) < 0:
         self.liveTVRecorder = None
         return None
         
      # TODO Check that recorder is not slave backend - that is not supported
      
      self.currentChannel = self.mythDB.getCardInput(self.liveTVRecorder).startchan
         
      args = '[]:[]SPAWN_LIVETV[]:[]live-' + socket.gethostname() + '-' + datetime.datetime.today().isoformat()
      args += '[]:[]0[]:[]' + self.currentChannel
      response = self.sendCommand(self.query() + args)
      if not response.startswith('ok'):
         print 'Failed to start live tv'
         self.stopLiveTV()
         return None
      
      return self.getCurrentRecording(callback)
         
         
   def changeChannel(self, channel, callback = None):
      # TODO Need to check this at some point
      response = self.sendCommand(self.query() + '[]:[]SHOULD_SWITCH_CARD[]:[]3032')
      response = self.sendCommand(self.query() + '[]:[]PAUSE')
      response = self.sendCommand(self.query() + '[]:[]CHECK_CHANNEL[]:[]' + channel)
      response = self.sendCommand(self.query() + '[]:[]SET_CHANNEL[]:[]' + channel)
      self.currentChannel = channel
      return self.getCurrentRecording(callback)
         
         
   def getCurrentRecording(self, callback = None):
      if self.waitForRecording():
         # For some reason Myth returns a wrong filename if we do the next step immediately
         # Fortunately, we should wait a few seconds to let it get ahead anyway
         start = time.time()
         while time.time() - start < 5:
            time.sleep(.1)
            if callback is not None:
               callback()
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
         
      self.liveTVRecorder = None
      
      
   def query(self):
      return 'QUERY_RECORDER ' + self.liveTVRecorder
      
      
   def deleteProgram(self, program, forget):
      """I think this is the proper syntax for this command, but I'm not 100% sure.  Myth isn't
      complaining about it when I send it, but my testing suggests that it forces deletion
      whether I include the FORCE option or not, and the FORGET is difficult to test."""
      ts = program.starttime.strftime('%Y%m%d%H%M%S')
      command = 'DELETE_RECORDING ' + str(program.chanid) + ' ' + ts + ' FORCE'
      if forget:
         command += ' FORGET'
      self.sendCommand(command)
      