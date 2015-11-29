from flask import Flask

def create_app():
	app = Flask(__name__)

	import os
	app.config.from_object(os.environ['APP_SETTINGS'])

	from .core import redis
	redis.init_app(app)

	from .tasks import TasksView
	TasksView.register(app)

	from .handlers import not_found, bad_request, internal_error
	app.register_error_handler(404, not_found)
	app.register_error_handler(400, bad_request)
	app.register_error_handler(500, internal_error)

	return app