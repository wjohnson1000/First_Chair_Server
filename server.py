from flask import *
from flask.ext.cors import CORS
from operator import itemgetter, attrgetter, methodcaller
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
  is_destination = Column(Boolean, default=False)

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
google_client_key = os.environ.get("GOOGLE_CLIENT_KEY")
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
    #return redirect('http://firstchair.club/#/dashboard')


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
    return redirect('http://127.0.0.1:8080/#/dashboard?token=' + token)
#    return redirect('http://firstchair.club/#/dashboard?token=' + token)

@app.route("/dashboard")
def routeInfo():
  places = []
  this_user = sesh.query(user).first()
  home = sesh.query(place).filter(place.id == this_user.place_id).first()
  user_places = sesh.query(user_place).filter(user_place.user_id == this_user.id).all()
  for destination in user_places:
    destination = sesh.query(place).filter(place.id == destination.place_id).one()
    directionstring = 'https://www.google.com/maps/embed/v1/directions?origin=' + home.address + '+' + home.city + '+' + home.state + '&destination=' + destination.address + '+' + destination.city + '+' + destination.state + '&key=' + google_client_key
    accumulations = sesh.query(snowfall).filter(snowfall.place_id == destination.id).all()
    drives = sesh.query(travel_time).filter(travel_time.place_id == destination.id).all()
    allsnowfall = [];
    for accumulation in accumulations:
      allsnowfall.append(accumulation.snowfall);
    drive_time = [];
    for drive in drives:
      drive_time.append(drive.travel_time/60);
    graphData = [];
    for i in range(len(drive_time) - 1):
      graphData.append({'snowfall': allsnowfall[i], 'nextdaydrive': drive_time[i+1]})
    graphData = sorted(graphData, key=lambda x: x['snowfall'])
    basevalue = 0
    basecount = 0
    for i in range(len(graphData)):
      if graphData[i]['snowfall'] == 0:
        basevalue = basevalue + graphData[i]['nextdaydrive']
        basecount = basecount + 1
      if graphData[i - 1]['snowfall'] == 0 and graphData[i]['snowfall'] != 0:
        graphData[i - 1]['nextdaydrive'] = basevalue / basecount
    graphData = graphData[basecount-1:len(graphData)]
    forecast = unirest.get("http://api.wunderground.com/api/" + weather_key + "/forecast/q/" + destination.state + "/" + destination.city + ".json")
    dest_obj = {}
    dest_obj['directionstring'] = directionstring
    dest_obj['forecast'] = forecast.body['forecast']['simpleforecast']['forecastday'][0]['snow_allday']
    dest_obj['address'] = destination.address
    dest_obj['city'] = destination.city
    dest_obj['state'] = destination.state
    dest_obj['snowfall'] = allsnowfall
    dest_obj['travel_time'] = drive_time
    dest_obj['graph_data'] = graphData
    places.append(dest_obj)
  return jsonify({'destinations': places})


@app.route("/findroute", methods=['GET', 'POST'])
def findroute():
  if request.method == 'POST':
    guesses = unirest.get("https://maps.googleapis.com/maps/api/place/textsearch/json?query=" + request.data +"&key=AIzaSyC9CWQ9sZa0uVd0sYs-qo1K-xzq2jYH0qE")
    print request.data
    return jsonify(guesses.body)

@app.route("/addroute", methods=['GET', 'POST'])
def addRoute():
  if request.method == 'POST':
    print request.data.destination.formatted_address
    print request.data.destination.name
    add_route_city = ""
    add_route_state = ""
    commacount = 0
    for char in request.data.destination.formatted_address:
      if char == ",":
        commacount = commacount + 1
        continue
      if commacount == 1:
        add_route_city = add_route_city + char
      if commacount == 2:
        add_route_state = add_route_state + char
    print add_route_city 
    print add_route_state 
    add_route_address = request.data.destination.name
    this_user = sesh.query(user).first()
    new_dest = place(address = add_route_address, city = add_route_city, state = add_route_state)
    sesh.add(new_dest)
    sesh.commit()
    
    return "New Route Added"
    
if __name__ == "__main__":
  PORT = int(os.environ.get("PORT", 5000))
  import uuid
  app.secret_key = str(uuid.uuid4())
  #app.run(port=PORT, debug=True)
  #0.0.0.0 FOR HEROKU
  app.run(host='0.0.0.0', port=PORT, debug=True)

