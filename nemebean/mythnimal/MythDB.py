from MySQLdb import connect, paramstyle

class MythDB:
   def __init__(self, host, user, password):
      self.db = connect(host, user, password, 'mythconverg')
      
   
   def showList(self):
      c = self.db.cursor()
      c.execute('select title from recorded group by title')
      return c.fetchall()
      
   def programList(self, title):
      c = self.db.cursor()
      query = 'select basename, title, subtitle, description, starttime '
      query += 'from recorded '
      query += 'where title like %s '
      query += 'order by starttime desc'
      c.execute(query, title)
      return c.fetchall()
      