from flask import Flask

def create_app():
	app = Flask(__name__)

	import os
	app.config.from_object(os.environ['APP_SETTINGS'])

	from .core import redis
	redis.init_app(app)

	from .tasks import tasks
	app.register_blueprint(tasks)

	return app