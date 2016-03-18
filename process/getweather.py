#import processconfig as api_config
#import db_config as db_config
import modules.processconfig as api_config
#import db.db_config as db_config
import unirest
import os
import psycopg2
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base

#weather_key = os.environ.get("WUNDERGROUND_API_KEY")
weather_key = api_config.api_key['wunderground']
#db_url = os.environ.get("DATABASE_URL")
db_url = "postgres://localhost/firstchair"

Base = declarative_base()
class place(Base):
  __tablename__ = 'place'

  id = Column(Integer, primary_key=True)
  address = Column(String)
  city = Column(String)
  state = Column(String(10))

engine = create_engine(db_url, echo=True)
connection = engine.connect()
Session = sessionmaker(bind=engine)
session = Session()
#print response.body

#USE SESSION.COMMIT() FOR MASS TRX?

for place in session.query(place):
  response = unirest.get("http://api.wunderground.com/api/" + weather_key + "/conditions/q/" + place.state + "/" + place.city + ".json")
  print response.body
