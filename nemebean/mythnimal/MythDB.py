#from MySQLdb import connect, paramstyle
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class MythDB:
   def __init__(self, host, user, password):
      self.engine = create_engine('mysql://' + user + ':' + password + '@' + host + '/mythconverg')
      Session = sessionmaker(bind=self.engine)
      self.session = Session()
      
   
   def showList(self):
      retval = self.session.query(Program).group_by(Program.title).all()
      return retval
      
      
   def programList(self, title):
      retval = self.session.query(Program).filter(Program.title.like(title)).order_by(Program.starttime.desc()).all()
      return retval

      
   def skipList(self, filename):
      program = self.session.query(Program).filter(Program.basename.like(filename)).first()
      starts = self.session.query(Markup).filter(Markup.chanid == program.chanid, \
                                                 Markup.starttime == program.starttime, \
                                                 Markup.type == 4) \
                                         .order_by(Markup.mark) \
                                         .all()
      ends = self.session.query(Markup).filter(Markup.chanid == program.chanid, \
                                               Markup.starttime == program.starttime, \
                                               Markup.type == 5) \
                                       .order_by(Markup.mark) \
                                       .all()
      startret = [i.mark for i in starts]
      endret = [i.mark for i in ends]
      return (startret, endret)

      
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
   
   def __init__(self, title = ''):
      self.title = title
      
      
class Markup(Base):
   __tablename__ = 'recordedmarkup'
   chanid = Column(Integer, primary_key=True)
   starttime = Column(DateTime, primary_key=True)
   mark = Column(Integer, primary_key=True)
   type = Column(Integer, primary_key=True)