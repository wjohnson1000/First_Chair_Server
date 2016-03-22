from flask import *
from flask.ext.cors import CORS
import jwt
import os
import json
import httplib2
import unirest
from apiclient import discovery
from oauth2client import client as client
from oauth2client.contrib.flask_util import UserOAuth2
import datetime
import psycopg2
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base

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

class snowfall(Base):
  __tablename__ = 'snowfall'
  id = Column(Integer, primary_key=True)
  place_id = Column(Integer, ForeignKey('place.id'))
  snowfall = Column(Integer)
  time = Column(DateTime, default=datetime.datetime.now)

weather_key = os.environ.get("WUNDERGROUND_API_KEY")
google_key = os.environ.get("GOOGLE_API_KEY")
db_url = os.environ.get("DATABASE_URL")


client_info = {
  "web": {
    "client_id": os.environ.get("client_id"),
    "Project_id": os.environ.get("Project_id"),
    "auth_uri": os.environ.get("auth_uri"),
    "token_uri": os.environ.get("token_uri"),
    "auth_provider_x509_cert_url": os.environ.get("auth_provider_x509_cert_url"),
    "client_secret": os.environ.get("client_secret"),
    "redirect_uris":[os.environ.get("redirect_uris")]
  }
}

with open('secrets_from_env.json', 'w') as f:
  json.dump(client_info, f)

app = Flask(__name__)
CORS(app)

engine = create_engine(db_url, echo=True)
connection = engine.connect()
Session = sessionmaker(bind=engine)
sesh = Session()

@app.route("/")
def index():
  if 'credentials' not in session:
    return redirect(url_for('oauth2callback'))
  credentials = client.OAuth2Credentials.from_json(session['credentials'])
  if credentials.access_token_expired:
    return redirect(flask.url_for('oauth2callback'))
  else:
    return redirect('http://127.0.0.1:8080/#/dashboard')


@app.route('/callback')
def oauth2callback():
  flow = client.flow_from_clientsecrets('secrets_from_env.json',
    scope='https://www.googleapis.com/auth/plus.login',
    redirect_uri=url_for('oauth2callback', _external=True))
  if 'code' not in request.args:
    auth_uri = flow.step1_get_authorize_url()
    return redirect(auth_uri)
  else:
    auth_code = request.args.get('code')
    token = jwt.encode({'auth_code': auth_code}, 'secret', algorithm='HS256')
    credentials = flow.step2_exchange(auth_code)
    session['credentials'] = credentials.to_json()
    #return resp
    return redirect('http://127.0.0.1:8080/#/dashboard?token=' + token)

@app.route("/dashboard")
def routeInfo():
  places = []
  this_user = sesh.query(user).first()
  user_places = sesh.query(user_place).filter(user_place.user_id == this_user.id).all()
  for destination in user_places:
    destination = sesh.query(place).filter(place.id == destination.place_id).one()
    accumulations = sesh.query(snowfall).filter(snowfall.place_id == destination.id).all()
    drives = sesh.query(travel_time).filter(travel_time.place_id == destination.id).all()
    allsnowfall = [];
    for accumulation in accumulations:
      allsnowfall.append(accumulation.snowfall);
    drive_time = [];
    for drive in drives:
      drive_time.append(drive.travel_time);
    forecast = unirest.get("http://api.wunderground.com/api/" + weather_key + "/forecast/q/" + destination.state + "/" + destination.city + ".json")
    dest_obj = {}
    dest_obj['forecast'] = forecast.body['forecast']['simpleforecast']['forecastday'][0]['snow_allday']
    dest_obj['address'] = destination.address
    dest_obj['city'] = destination.city
    dest_obj['state'] = destination.state
    dest_obj['snowfall'] = allsnowfall
    dest_obj['travel_time'] = drive_time
    places.append(dest_obj)
  return jsonify({'destinations': places})


#@app.route("/addroute")
#def routeInfo():
  

if __name__ == "__main__":
  PORT = int(os.environ.get("PORT", 5000))
  import uuid
  app.secret_key = str(uuid.uuid4())
  #app.run(port=PORT, debug=True)
  #0.0.0.0 FOR HEROKU
  app.run(host='0.0.0.0', port=PORT, debug=True)

