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
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from MythDBObjects import *

class MythDB:
   # Schema versions above this have not been verified to work
   supportedSchemas = [1264]
   def __init__(self, host, user, password):
      self.engine = create_engine('mysql://' + user + ':' + password + '@' + host + '/mythconverg')
      
      
      Session = sessionmaker(bind=self.engine)
      self.session = Session()
      
      self.writes = False
      schemaVersion = int(self.session.query(Settings).filter(Settings.value == 'DBSchemaVer').first().data)
      # If not a supported schema, don't write to DB to avoid possible corruption
      if schemaVersion <= self.supportedSchemas[-1]:
         self.writes = True
      
   
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
      
      startret = [i.mark for i in starts]
      endret = [i.mark for i in ends]
      return (startret, endret)
      
      
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
      newMark = int(float(mplayer.position) * mplayer.fps)
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
      
      
   def commit(self):
      """self.session.commit should never be used directly, so that writes to an unsupported
      DB schema do not happen."""
      if self.writes:
         self.session.commit()
      else:
         print 'Warning: Unsupported DB schema.  Not committing changes'
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
                                        
                                        
   def getProgramSchedule(self, chanId, startTime, endTime):
      return self.session.query(ProgramSchedule).filter(ProgramSchedule.chanid == chanId) \
                                                .filter(ProgramSchedule.endtime > startTime) \
                                                .filter(ProgramSchedule.starttime < endTime) \
                                                .order_by(ProgramSchedule.chanid) \
                                                .all()

      
