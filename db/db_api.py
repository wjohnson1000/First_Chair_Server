import sys
import psycopg2
sys.path.append("Users/Billy/Git/First_Chair_Server/db")

from sqlalchemy import *
engine = create_engine('postgresql://localhost/broncos')
connection = engine.connect()
result = connection.execute("select * from roster")
for row in result:
  print row.player_name
connection.close()
print "connection closed"
