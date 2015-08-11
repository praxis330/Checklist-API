import os

class Config(object):
	USERNAME = os.environ.get('USER')
	PASSWORD = os.environ.get('PASSWORD')
	DEBUG = False
	TESTING = False
	CSRF_ENABLED = True

class ProductionConfig(Config):
	DEBUG = False

class DevelopmentConfig(Config):
	DEVELOPMENT = True
	DEBUG = True