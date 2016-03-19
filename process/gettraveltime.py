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
  is_destination = Column(Boolean)

class user(Base):
  __tablename__ = 'user'
  id = Column(Integer, primary_key=True)
  google_id = Column(Integer)
  snowfall_alarm = Column(Integer)
  travel_window = Column(String(10))
  place_id = Column(Integer, ForeignKey('place.id'))

class user_place(Base):
  __tablename__ = 'user_place'
  user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
  place_id = Column(Integer, ForeignKey('place.id'), primary_key=True)

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

users = session.query(user).all()
for user in users:
  homeid =  user.place_id
  print homeid
  home = session.query(place).filter(place.id == homeid).one()
  print home.city
  destinations = session.query(user_place).filter(user_place.user_id == user.id).all()
  for destination in destinations:
    destination = session.query(place).filter(place.id == destination.place_id).one()
    print destination.city
  
    gresponse = unirest.get("https://maps.googleapis.com/maps/api/distancematrix/json?origins=" + home.address + "+" + home.city + "+" + home.state + "&destinations=" + destination.address + "+" + destination.city + "+" + destination.state + "&key=" + google_key)
    
    trip_time = gresponse.body['rows'][0]['elements'][0]['duration']['value']
    print trip_time 
    trip = travel_time(place_id = destination.id, user_id = user.id, travel_time = trip_time)
    session.add(trip)

session.commit()
