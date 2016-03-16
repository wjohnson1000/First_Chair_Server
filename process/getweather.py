import processconfig
response = unirest.get("http://api.wunderground.com/api/" + processconfig.api_key['wunderground'] + "/conditions/q/CO/Denver.json")
print response.body
