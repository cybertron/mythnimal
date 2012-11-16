from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
Base = declarative_base()

class Program(Base):
   __tablename__ = 'recorded'
   basename = Column(String, primary_key=True)
   title = Column(String)
   subtitle = Column(String)
   description = Column(String)
   starttime = Column(DateTime)
   endtime = Column(DateTime)
   chanid = Column(Integer)
   bookmark = Column(Integer)
   
   def __init__(self, title = ''):
      self.title = title
      
   def __repr__(self):
      return 'Program(' + self.basename + '\n' + self.title + '\n' + self.subtitle + '\n' + self.description + '\n' + \
             str(self.starttime) + '\n' + str(self.endtime) + '\n' + str(self.chanid) + '\n' + str(self.bookmark) + ')'
      
      
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
   