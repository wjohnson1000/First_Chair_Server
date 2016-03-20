from flask import *
import jwt
import os
import json
import httplib2
import clientconfig
from apiclient import discovery
from oauth2client import client as client

app = Flask(__name__)

#for DEPLOYMENT
#flow = OAuth2WebServerFlow(client_id='your_client_id',
#                           client_secret='your_client_secret',
#                           scope='https://www.googleapis.com/auth/calendar',
#                           redirect_uri='http://example.com/auth_return')



@app.route("/")
def index():
  if 'credentials' not in session:
    return redirect(url_for('oauth2callback'))
  credentials = client.OAuth2Credentials.from_json(session['credentials'])
  if credentials.access_token_expired:
    return redirect(flask.url_for('oauth2callback'))
  else:
    return "authorized"


@app.route('/callback')
def oauth2callback():
  flow = client.flow_from_clientsecrets('client_secrets.json',
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
    return redirect(url_for('index'))

if __name__ == "__main__":
  PORT = int(os.environ.get("PORT", 5000))
  import uuid
  app.secret_key = str(uuid.uuid4())
  #app.run(port=PORT, debug=True)
  #0.0.0.0 FOR HEROKU
  app.run(host='0.0.0.0', port=PORT)

