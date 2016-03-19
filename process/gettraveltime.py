#import sys
#sys.path.append("Users/Billy/Git/First_Chair_Server/process")
#import processconfig as config #for local testing
import unirest
import os
import datetime
import psycopg2
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base

google_key = os.environ.get("GOOGLE_API_KEY")
db_url = os.environ.get("DATABASE_URL")

Base = declarative_base()

class place(Base):
  __tablename__ = 'place'
  id = Column(Integer, primary_key=True)
  address = Column(String)
  city = Column(String)
  state = Column(String(10))

class user(Base):
  __tablename__ = 'user'
  id = Column(Integer, primary_key=True)
  google_id = Column(Integer)
  snowfall_alarm = Column(Integer)
  travel_window = Column(String(10))
  place_id = Column(Integer, ForeignKey('place.id'))

class travel_time(Base):
  __tablename__ = 'travel_time'
  id = Column(Integer, primary_key=True)
  place_id = Column(Integer, ForeignKey('place.id'))
  user_id = Column(Integer, ForeignKey('user.id'))
  travel_time = Column(Integer)
  time = Column(DateTime, default=datetime.datetime.now)
  

engine = create_engine(db_url, echo=True)
connection = engine.connect()
Session = sessionmaker(bind=engine)
session = Session()

selecteduser = session.query(user).first()
homeid =  selecteduser.place_id
print homeid
destination = session.query(place).filter(place.id == 2)
print destination.id

#gresponse = unirest.get("https://maps.googleapis.com/maps/api/distancematrix/json?origins=" + home.address + "+" + home.city + "+" + home.state + "&destinations=" + destination.address + "+" + destination.city + "+" + destination.state + "&key=" + google_key)

#print gresponse.body
