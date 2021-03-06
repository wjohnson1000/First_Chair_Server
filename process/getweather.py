import datetime
import unirest
import os
import psycopg2
from random import randint
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base

weather_key = os.environ.get("WUNDERGROUND_API_KEY")
db_url = os.environ.get("DATABASE_URL")
#weather_key = api_config.api_key['wunderground']
#db_url = "postgres://localhost/firstchair"

Base = declarative_base()
class place(Base):
  __tablename__ = 'place'

  id = Column(Integer, primary_key=True)
  address = Column(String)
  city = Column(String)
  state = Column(String(10))

class snowfall(Base):
  __tablename__ = 'snowfall'

  id = Column(Integer, primary_key=True)
  place_id = Column(Integer, ForeignKey('place.id'))
  snowfall = Column(Integer)
  time = Column(DateTime, default=datetime.datetime.now)

engine = create_engine(db_url, echo=True)
connection = engine.connect()
Session = sessionmaker(bind=engine)
session = Session()


for place in session.query(place):
#  response = unirest.get("http://api.wunderground.com/api/" + weather_key + "/conditions/q/" + place.state + "/" + place.city + ".json")
#  snow = response.body['current_observation']['precip_1hr_in']
  snow = randint(0,10)
  session.add(snowfall(place_id=place.id, snowfall=snow))
  print snow

session.commit()

connection.close()

