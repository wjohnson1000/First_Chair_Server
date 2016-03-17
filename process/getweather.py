import sys
#sys.path.append("Users/Billy/Git/First_Chair_Server/process")
#sys.path.append("Users/Billy/Git/First_Chair_Server/db")
#print sys.path
#import processconfig as api_config
#import db.db_config as db_config
import process.processconfig as api_config
import db.db_config as db_config
import unirest
import psycopg2
from sqlalchemy import *

#meta = MetaData()
engine = create_engine(db_config.db_var['url'])
connection = engine.connect()
response = unirest.get("http://api.wunderground.com/api/" + api_config.api_key['wunderground'] + "/conditions/q/CO/Denver.json")
print response.body
