from flask import *
from flask.ext.cors import CORS
from flask.ext.session import Session
from operator import itemgetter, attrgetter, methodcaller
import jwt
import os
import json
import httplib2
import unirest
import uuid
from apiclient.discovery import build
from oauth2client import client as client
from oauth2client.contrib.flask_util import *
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
  is_destination = Column(Boolean, default=True)

class user(Base):
  __tablename__ = 'user'
  id = Column(Integer, primary_key=True)
  google_id = Column(Integer)
  snowfall_alarm = Column(Integer)
  travel_window = Column(String(10), default='morning')
  place_id = Column(Integer, ForeignKey('place.id'))
  set_home = Column(Boolean, default=False)

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

#app.config['SESSION_TYPE'] = 'null'
#app.secret_key = str(uuid.uuid4())
app.config['GOOGLE_OAUTH2_CLIENT_SECRETS_FILE'] = 'secrets_from_env.json'

oauth2 = UserOAuth2(app)

engine = create_engine(db_url, echo=True)
connection = engine.connect()
SQLSession = sessionmaker(bind=engine)
sesh = SQLSession()

mysecret = str(uuid.uuid4())

@app.before_request
def check_cred():
  if str(request.url_rule) != '/callback' and str(request.url_rule) != '/logout':
    print 'in the if'
    print request.headers.get('Authorization')
    if request.headers.get('Authorization') is None:
      redirect(url_for('oauth2callback'))
    else:
      token_from_client = request.headers[('Authorization')]
      try:
        print "can i decode"
        payload = jwt.decode(token_from_client, mysecret)
      except jwt.InvalidTokenError:
        print 'invalid token error'
        redirect(url_for('oauth2callback'))

@app.route("/")
def index():
  return redirect('http://firstchair.club/#/dashboard')

@app.route('/callback')
def oauth2callback():
  flow = client.flow_from_clientsecrets('secrets_from_env.json',
    scope='profile',
    redirect_uri=url_for('oauth2callback', _external=True))
  if 'code' not in request.args:
    auth_uri = flow.step1_get_authorize_url()
    return redirect(auth_uri)
  else:
    auth_code = request.args.get('code')
    credentials = flow.step2_exchange(auth_code)
    http_auth = credentials.authorize(httplib2.Http())
    user_info = build('oauth2', 'v2', http=http_auth)
    user_obj = user_info.userinfo().v2().me().get().execute()
    goog_id = str(user_obj['id'])
    my_jwt = jwt.encode({'google_id': goog_id}, mysecret, algorithm='HS256')
    if sesh.query(user).filter(user.google_id == goog_id).first() == None:
      sesh.add(user(google_id=goog_id, snowfall_alarm=5, place_id=1))
      sesh.commit()
    else:
      print 'got em'
    return redirect('http://firstchair.club/#/dashboard?token=' + my_jwt)

@app.route("/dashboard")
def routeInfo():
  token_from_client = request.headers[('Authorization')]
  goog_id = jwt.decode(token_from_client, mysecret, algorithm='HS256')
  goog_id = str(goog_id['google_id'])
  this_user = sesh.query(user).filter(user.google_id == goog_id).first()
  places = []
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
  return jsonify({'destinations': places, 'snowfall_alarm': this_user.snowfall_alarm, 'set_home': this_user.set_home})


@app.route("/findroute", methods=['GET', 'POST'])
def findroute():
  if request.method == 'POST':
    guesses = unirest.get("https://maps.googleapis.com/maps/api/place/textsearch/json?query=" + request.data +"&key=AIzaSyC9CWQ9sZa0uVd0sYs-qo1K-xzq2jYH0qE")
    print request.data
    return jsonify(guesses.body)

@app.route("/addroute", methods=['GET', 'POST'])
def addRoute():
  token_from_client = request.headers[('Authorization')]
  goog_id = jwt.decode(token_from_client, mysecret, algorithm='HS256')
  goog_id = str(goog_id['google_id'])
  this_user = sesh.query(user).filter(user.google_id == goog_id).first()
  if request.method == 'POST':
    formatted_address  = request.get_json()['desty']['formatted_address']
    name = request.get_json()['desty']['name']
    print formatted_address
    print name
    add_route_city = ""
    add_route_state = ""
    commacount = 0
    for char in formatted_address:
      if char == ",":
        commacount = commacount + 1
        continue
      if commacount == 1:
        add_route_city = add_route_city + char
      if commacount == 2:
        add_route_state = add_route_state + char
    print add_route_city 
    print add_route_state 
    new_place = place(address = name, city = add_route_city, state = add_route_state)
    sesh.add(new_place)
    sesh.commit()
    get_new_place = sesh.query(place).order_by(place.id.desc()).first()
    new_user_place = user_place(user_id = this_user.id, place_id = get_new_place.id)
    sesh.add(new_user_place)
    sesh.commit()
    return "New Route Added"

@app.route("/setalarm", methods=['PUT'])
def setAlarm():
  token_from_client = request.headers[('Authorization')]
  goog_id = jwt.decode(token_from_client, mysecret, algorithm='HS256')
  goog_id = str(goog_id['google_id'])
  this_user = sesh.query(user).filter(user.google_id == goog_id).first()
  set_alarm = request.get_json()['alarm']
  print set_alarm
  this_user.snowfall_alarm = set_alarm
  sesh.commit()
  return 'alarm updated'

@app.route('/sethome', methods=['POST'])
def sethome():
  token_from_client = request.headers[('Authorization')]
  goog_id = jwt.decode(token_from_client, mysecret, algorithm='HS256')
  goog_id = str(goog_id['google_id'])
  this_user = sesh.query(user).filter(user.google_id == goog_id).first()
  home_address = request.get_json()['address']
  home_city = request.get_json()['city']
  home_state = request.get_json()['state']
  this_user_home = place(address = home_address, city = home_city, state = home_state, is_destination = False)
  sesh.add(this_user_home)
  sesh.commit()
  user_home_in_db = sesh.query(place).filter(place.address == this_user_home.address, place.city == this_user_home.city).first()
  this_user.place_id = user_home_in_db.id
  this_user.set_home = True
  sesh.commit()
  return 'home address set'

if __name__ == "__main__":
  PORT = int(os.environ.get("PORT", 5000))
  #app.run(port=PORT, debug=True)
  #0.0.0.0 FOR HEROKU
  app.run(host='0.0.0.0', port=PORT, debug=True)

