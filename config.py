import os

class Config(object):
	DEBUG = False
	TESTING = False
	CSRF_ENABLED = True

class ProductionConfig(Config):
	REDIS_URL = os.environ.get('REDISCLOUD_URL')
	DEBUG = False

class DevelopmentConfig(Config):
	REDIS_URL = os.environ.get('REDIS_URL')
	DEVELOPMENT = True
	DEBUG = True

