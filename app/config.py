import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

class Config(object):
	DEBUG = False
	TESTING = False
	CSRF_ENABLED = True

class ProductionConfig(Config):
	DEBUG = False

class DevelopmentConfig(Config):
	DEVELOPMENT = True
	DEBUG = True