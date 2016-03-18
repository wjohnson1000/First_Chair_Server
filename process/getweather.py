#import processconfig as api_config
#import db_config as db_config
#import process.processconfig as api_config
#import db.db_config as db_config
import unirest
import os
import psycopg2
from sqlalchemy import *
from sqlalchemy.orm import *
weather_key = os.environ.get("WUNDERGROUND_API_KEY")
#db_url = os.environ.get("DATABASE_URL")
db_url = "postgres://localhost/firstchair"
engine = create_engine(db_url, echo=True)
connection = engine.connect()
Session = sessionmaker(bind=engine)
session = Session()
#response = unirest.get("http://api.wunderground.com/api/" + weather_key + "/conditions/q/CO/Denver.json")
#print response.body

#USE SESSION.COMMIT() FOR MASS TRX?

for instance in session.query(place):
  print instance
