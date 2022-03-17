import json
import requests

class MythService:
   def __init__(self):
      pass

   def send(self, path):
      headers = {'Accept': 'application/json'}
      r = requests.get(f'http://11.1.1.4:6544/{path}',
                      headers=headers)
      return r.json()

   def showList(self):
      shows = self.send('Dvr/GetRecordedList')
      shows = shows['ProgramList']['Programs']
      shows = [i['Title'] for i in shows]
      shows = list(set(shows))
      shows.sort()
      return shows

   def programList(self, showFilter):
      programs = self.send('Dvr/GetRecordedList')
      programs = programs['ProgramList']['Programs']
      programs.sort(key=lambda x: x['StartTime'])
      programs.reverse()
      return programs
