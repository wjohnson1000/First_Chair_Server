import sys
sys.path.append("Users/Billy/Git/First_Chair_Server/process")
sys.path.append("Users/Billy/Git/First_Chair_Server/db")
import psycopg2
import db.db_config as db_config
import process.processconfig as api_config
import unirest
from sqlalchemy import *

#meta = MetaData()
engine = create_engine(db_config.db_var['url'])
connection = engine.connect()
response = unirest.get("http://api.wunderground.com/api/" + api_config.api_key['wunderground'] + "/conditions/q/CO/Denver.json")
print response.body
