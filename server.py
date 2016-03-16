from flask import Flask
import unirest
import config
app = Flask(__name__)

#response = unirest.get("http://api.wunderground.com/api/" + config.api_key['wunderground'] + "/conditions/q/CO/Denver.json")
#gresponse = unirest.get("https://maps.googleapis.com/maps/api/distancematrix/json?origins=Vancouver+BC|Seattle&destinations=San+Francisco|Victoria+BC&key=" + config.api_key['google'])
#print response.body

@app.route("/")
def hello():
    return response

if __name__ == "__main__":
    app.run()
