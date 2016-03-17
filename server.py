from flask import Flask
import os
#import unirest
PORT = 'PORT'
app = Flask(__name__)

#gresponse = unirest.get("https://maps.googleapis.com/maps/api/distancematrix/json?origins=Vancouver+BC|Seattle&destinations=San+Francisco|Victoria+BC&key=" + config.api_key['google'])
#print response.body

@app.route("/")
def hello():
    return "Hello World"

if __name__ == "__main__":
    port = int(os.environ.get('$PORT', 5000))
    app.run(host='0.0.0.0', port=PORT)
