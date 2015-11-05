from flask import Flask

def create_app():
	app = Flask(__name__)

	import os
	app.config.from_object(os.environ['APP_SETTINGS'])

	from urlparse import urlparse
	from redis import Redis
	url = urlparse(app.config['REDIS_URL'])
	redis_db = Redis(host=url.hostname, port=url.port, password=url.password)

	return app