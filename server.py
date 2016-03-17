from flask import Flask
#import unirest
app = Flask(__name__)

#gresponse = unirest.get("https://maps.googleapis.com/maps/api/distancematrix/json?origins=Vancouver+BC|Seattle&destinations=San+Francisco|Victoria+BC&key=" + config.api_key['google'])
#print response.body

@app.route("/")
def hello():
    return "Hello World"

if __name__ == "__main__":
    app.run()
