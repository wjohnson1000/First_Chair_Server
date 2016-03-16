import sys
sys.path.append("Users/Billy/Git/First_Chair_Server/process")
print sys.path
import processconfig
import unirest
response = unirest.get("http://api.wunderground.com/api/" + processconfig.api_key['wunderground'] + "/conditions/q/CO/Denver.json")
print response.body
