from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

class MythDB:
   # Schema versions above this have not been verified to work
   supportedSchema = 1264
   def __init__(self, host, user, password):
      self.engine = create_engine('mysql://' + user + ':' + password + '@' + host + '/mythconverg')
      Session = sessionmaker(bind=self.engine)
      self.session = Session()
      
      self.writes = False
      schemaVersion = int(self.session.query(Settings).filter(Settings.value == 'DBSchemaVer').first().data)
      # If not a supported schema, don't write to DB to avoid possible corruption
      if schemaVersion <= self.supportedSchema:
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
      if self.writes:
         self.session.commit()
      else:
         print 'Warning: Unsupported DB schema.  Not committing changes'
         self.session.rollback()
      
      
   def getProgram(self, filename):
      return self.session.query(Program).filter(Program.basename.like(filename)).first()
      
   def getMarkup(self, program, type):
      return self.session.query(Markup).filter(Markup.chanid == program.chanid) \
                                       .filter(Markup.starttime == program.starttime) \
                                       .filter(Markup.type == type) \
                                       .order_by(Markup.mark) \
                                       .all()
   
   def getChannel(self, chanid):
      channel = self.session.query(Channel).filter(Channel.chanid == chanid).first()
      if channel is not None:
         return channel
      return Channel()

      
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
   