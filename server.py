from flask import *
import jwt
import os
import json
import httplib2
#import clientconfig
from apiclient import discovery
from oauth2client import client as client
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


@app.route("/")
def index():
  if 'credentials' not in session:
    return redirect(url_for('oauth2callback'))
  credentials = client.OAuth2Credentials.from_json(session['credentials'])
  if credentials.access_token_expired:
    return redirect(flask.url_for('oauth2callback'))
  else:
    return flask.jsonify(credentials)

@app.route("/route")
def routeInfo():
  engine = create_engine(db_url, echo=True)
  connection = engine.connect()
  Session = sessionmaker(bind=engine)
  session = Session()
  user = session.query(user).first()
  print user
  destinations = session.query(user_place).filter(user_place.user_id == user.id).all()
  return "hey"

@app.route('/callback')
def oauth2callback():
  flow = client.flow_from_clientsecrets('secrets_from_env.json',
    scope='https://www.googleapis.com/auth/plus.login',
    redirect_uri=url_for('oauth2callback', _external=True))
  if 'code' not in request.args:
    auth_uri = flow.step1_get_authorize_url()
    return auth_uri
  else:
    auth_code = request.args.get('code')
    token = jwt.encode({'auth_code': auth_code}, 'secret', algorithm='HS256')
    credentials = flow.step2_exchange(auth_code)
    session['credentials'] = credentials.to_json()
    #return resp
    return redirect('127.0.0.1:8080&token=' + token)

if __name__ == "__main__":
  PORT = int(os.environ.get("PORT", 5000))
  import uuid
  app.secret_key = str(uuid.uuid4())
  #app.run(port=PORT, debug=True)
  #0.0.0.0 FOR HEROKU
  app.run(host='0.0.0.0', port=PORT)

