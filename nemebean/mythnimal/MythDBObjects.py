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
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
Base = declarative_base()

class Program(Base):
   __tablename__ = 'recorded'
   basename = Column(String, primary_key=True)
   title = Column(String)
   subtitle = Column(String)
   description = Column(String)
   recgroup = Column(String)
   starttime = Column(DateTime)
   endtime = Column(DateTime)
   chanid = Column(Integer)
   bookmark = Column(Integer)
   
   def __init__(self, title = ''):
      self.title = title
      
   def __repr__(self):
      return 'Program(' + self.basename + '\n' + self.title + '\n' + self.subtitle + '\n' + self.description + '\n' + \
             str(self.starttime) + '\n' + str(self.endtime) + '\n' + str(self.chanid) + '\n' + str(self.bookmark) + ')'
   
   def mythStart(self):
      return starttime.strftime('%Y%m%d%H%M%S')
      
      
class Markup(Base):
   __tablename__ = 'recordedmarkup'
   chanid = Column(Integer, primary_key=True)
   starttime = Column(DateTime, primary_key=True)
   mark = Column(Integer, primary_key=True)
   type = Column(Integer, primary_key=True)
   
   def __init__(self, program, mark, type):
      self.chanid = program.chanid
      self.starttime = program.starttime
      self.mark = mark
      self.type = type
      
   def __repr__(self):
      return 'Markup(' + str(self.chanid) + ', ' + str(self.starttime) + ', ' + str(self.mark) + ', ' + str(self.type) + ')'
      
      
class Settings(Base):
   __tablename__ = 'settings'
   value = Column(String, primary_key=True)
   data = Column(String)
   hostname = Column(String, primary_key=True)
   
   
class Channel(Base):
   __tablename__ = 'channel'
   chanid = Column(Integer, primary_key=True)
   channum = Column(String)
   callsign = Column(String)
   name = Column(String)
   sourceid = Column(Integer)
   
   def __init__(self):
      self.chanid = 0
      self.channum = 'NA'
      self.callsign = 'NA'
      self.name = 'NA'
      
      
class InUseProgram(Base):
   __tablename__ = 'inuseprograms'
   chanid = Column(Integer, primary_key=True)
   starttime = Column(DateTime, primary_key=True)
   recusage = Column(String, primary_key=True)
   
   
class CardInput(Base):
   __tablename__ = 'cardinput'
   cardid = Column(Integer, primary_key=True)
   sourceid = Column(Integer)
   startchan = Column(String)
   displayname = Column(String)
   
   
class TVChain(Base):
   __tablename__ = 'tvchain'
   chanid = Column(Integer, primary_key=True)
   starttime = Column(DateTime, primary_key=True)
   chainid = Column(String)
   chainpos = Column(Integer)
   cardtype = Column(String)
   
   
class ProgramSchedule(Base):
   __tablename__ = 'program'
   chanid = Column(Integer, primary_key = True)
   starttime = Column(DateTime, primary_key = True)
   endtime = Column(DateTime)
   title = Column(String)
   subtitle = Column(String)
   description = Column(String)
   originalairdate = Column(DateTime)
   manualid = Column(Integer, primary_key = True)
   
   def __repr__(self):
      return 'ProgramSchedule(' + str(self.chanid) + ', ' + str(self.starttime) + ', ' + str(self.endtime) + \
      ', ' + self.title + ', ' + self.subtitle + ', ' + self.description + ')'
   