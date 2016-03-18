import sys
import psycopg2
sys.path.append("Users/Billy/Git/First_Chair_Server/db")
import db_config as config
from sqlalchemy import *

meta = MetaData()
engine = create_engine(config.db_var['url'])
connection = engine.connect()

user = Table("user", meta,
  Column("id", Integer, primary_key=True),
  Column("google_id", Integer),
  Column("snowfall_alarm", Integer),
  Column("travel_window", String(10)),
  Column("place_id", Integer, ForeignKey("place.id"))
)

user_place = Table("user_place", meta,
  Column("user_id", Integer, ForeignKey("user.id")),
  Column("place_id", Integer, ForeignKey("place.id"))
)

place = Table("place", meta,
  Column("id", Integer, primary_key=True),
  Column("address", String),
  Column("city", String),
  Column("state", String(10)),
  Column("is_destination", Boolean)
)

snowfall = Table("snowfall", meta,
  Column("id", Integer, primary_key=True),
  Column("place_id", Integer, ForeignKey("place.id")),
  Column("snowfall", Integer),
  Column("time", DateTime, server_default=text('NOW()'))
)

travel_time = Table("travel_time", meta,
  Column("id", Integer, primary_key=True),
  Column("place_id", Integer, ForeignKey("place.id")),
  Column("user_id", Integer, ForeignKey("user.id")),
  Column("travel_time", Integer),
  Column("time", DateTime, server_default=text('NOW()'))
)

place.create(engine, checkfirst=True)
user.create(engine, checkfirst=True)
user_place.create(engine, checkfirst=True)
snowfall.create(engine, checkfirst=True)
travel_time.create(engine, checkfirst=True)
#connection.close()
print "schema migrated"
#result = connection.execute("select * from roster")
#for row in result:
#  print row.player_name
