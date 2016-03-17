import sys
sys.path.append("Users/Billy/Git/First_Chair_Server/process")
import process.processconfig as config #for heroku
#import processconfig as config #for local testing
import unirest
gresponse = unirest.get("https://maps.googleapis.com/maps/api/distancematrix/json?origins=Vancouver+BC|Seattle&destinations=San+Francisco|Victoria+BC&key=" + config.api_key['google'])
print gresponse.body
