from flask import Flask
import redis
import urlparse
import os

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])

#-------------------#
# Db initialisation #
#-------------------#

url = urlparse.urlparse(app.config['REDIS_URL'])
redis_db = redis.Redis(host=url.hostname, port=url.port, password=url.password)

# if not redis_db.exists("tasks:counter"):
# 	redis_db.set("tasks:counter", 0)

from app import views