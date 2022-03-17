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
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from PyQt5.QtCore import QTimer
import datetime
import os
from .MythDBObjects import *

class MythDB:
   # Schema versions not listed here may not work
   supportedSchemas = [1264, 1299, 1317, 1348]
   disableWrites = True
   def __init__(self, host, user, password):
      return
      self.engine = create_engine('mysql+pymysql://' + user + ':' + password + '@' + host + '/mythconverg')
      
      Session = sessionmaker(bind=self.engine)
      self.session = Session()
      
      self.writes = False
      self.schemaVersion = int(self.getSetting('DBSchemaVer'))
      # If not a supported schema, don't write to DB to avoid possible corruption
      if self.schemaVersion <= self.supportedSchemas[-1] and not self.disableWrites:
         self.writes = True
         
      # Ping the MySQL server periodically so our connection doesn't drop
      self.pingTimer = QTimer()
      pingInterval = 5 * 60 * 1000  # 5 minutes
      self.pingTimer.setInterval(pingInterval)
      self.pingTimer.timeout.connect(self.ping)
      self.pingTimer.start()
         
         
   def ping(self):
      return self.getSetting('DBSchemaVer')
      
   
   def showList(self):
      retval = self.session.query(Program).group_by(Program.title).all()
      return retval
      
      
   def programList(self, title):
      retval = self.session.query(Program).filter(Program.title.like(title)).order_by(Program.starttime.desc()).all()
      return retval

      
   def skipList(self, filename):
      program = self.getProgram(filename)
      starts = self.getMarkup(program, 4)
      ends = self.getMarkup(program, 5)
      framerate = self.framerate(program)
      
      startret = [i.mark for i in starts]
      endret = [i.mark for i in ends]
      
      return (startret, endret, framerate)
      
   def framerate(self, program):
      retval = self.getMarkup(program, 32)
      if not retval:
         return None
      # Myth stores its framerate in multiples of 1000
      fpsMult = 1000
      retval = float(retval[0].data) / float(fpsMult)
      return retval
      
      
   def programInUse(self, program):
      inUse = self.session.query(InUseProgram).filter(InUseProgram.chanid == program.chanid) \
                                              .filter(InUseProgram.starttime == program.starttime) \
                                              .all()
      for i in inUse:
         if i.recusage == 'recorder':
            return True
      return False
      
      
   def bookmark(self, filename):
      program = self.getProgram(filename)
      bookmark = self.getMarkup(program, 2)
      if len(bookmark) > 0:
         return bookmark[0].mark
      else:
         return 0
         
         
   def saveBookmark(self, mplayer, eof):
      program = self.getProgram(os.path.basename(mplayer.filename))
      bookmark = self.getMarkup(program, 2)
      framerate = self.framerate(program)
      if framerate is None:
         # Without a framerate the calculated bookmark value is meaningless
         return
      newMark = int(float(mplayer.position) * framerate)
      if eof:
         newMark = 0
      if len(bookmark) > 0:
         bookmark[0].mark = newMark
         self.session.add(bookmark[0])
      else:
         bookmark = Markup(program, newMark, 2)
         self.session.add(bookmark)
         program.bookmark = 1
         self.session.add(program)
         
      self.commit()
      
      
   def setRecGroup(self, program, value):
      program.recgroup = value
      self.session.add(program)
      self.commit()
      
      
   def commit(self):
      """self.session.commit should never be used directly so that writes to an unsupported
      DB schema do not happen."""
      if self.writes:
         self.session.commit()
      else:
         print('Warning: Unsupported DB schema.  Not committing changes')
         self.session.rollback()
      
      
   def getProgram(self, filename):
      return self.session.query(Program).filter(Program.basename.like(filename)).first()
      
   def getProgramByChain(self, chain):
      return self.session.query(Program).filter(Program.chanid == chain.chanid) \
                                        .filter(Program.starttime == chain.starttime) \
                                        .first()
      
   def getMarkup(self, program, type):
      return self.session.query(Markup).filter(Markup.chanid == program.chanid) \
                                       .filter(Markup.starttime == program.starttime) \
                                       .filter(Markup.type == type) \
                                       .order_by(Markup.mark) \
                                       .all()
   
   def getChannel(self, chanid):
      return self.session.query(Channel).filter(Channel.chanid == chanid).first()
      
   def getChannelByNum(self, num):
      return self.session.query(Channel).filter(Channel.channum == num).first()
      
   def getAllChannels(self):
      return self.session.query(Channel).order_by(Channel.channum).all()
      
      
   def getSetting(self, name):
      return self.session.query(Settings).filter(Settings.value == name).first().data
      
      
   def getCardInput(self, id):
      return self.session.query(CardInput).filter(CardInput.cardid == id).first()
      
   def getCardInputBySourceID(self, id):
      return self.session.query(CardInput).filter(CardInput.sourceid == id).all()
      
   def getTVChain(self, id):
      return self.session.query(TVChain).filter(TVChain.chainid == id) \
                                        .filter(TVChain.cardtype != 'DUMMY') \
                                        .order_by(TVChain.chainpos) \
                                        .all()
                                        
                                        
   def getProgramSchedule(self, startTime, endTime, chanId = None):
      if chanId is not None:
         return self.session.query(ProgramSchedule).filter(ProgramSchedule.chanid == chanId) \
                                                   .filter(ProgramSchedule.endtime > startTime) \
                                                   .filter(ProgramSchedule.starttime < endTime) \
                                                   .order_by(ProgramSchedule.chanid) \
                                                   .all()
      return self.session.query(ProgramSchedule).filter(ProgramSchedule.endtime > startTime) \
                                                .filter(ProgramSchedule.starttime < endTime) \
                                                .order_by(ProgramSchedule.chanid) \
                                                .all()
                                             
   def fromUTC(self, time):
      if self.isUTC():
         localTime = datetime.datetime.now()
         utcTime = datetime.datetime.utcnow()
         offset = localTime - utcTime
         return time + offset
      return time
      
   def isUTC(self):
      return True
      return self.schemaVersion > 1299

      
