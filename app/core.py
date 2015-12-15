from flask import make_response, jsonify
from flask.ext.httpauth import HTTPBasicAuth
from flask_redis import Redis
from .models import TaskManager, IndexManager, TaskValidator


redis = Redis()

index_manager = IndexManager(db=redis)

task_manager = TaskManager(db=redis, index=index_manager)

task_validator = TaskValidator()

auth = HTTPBasicAuth()


@auth.error_handler
def unauthorised():
    return make_response(jsonify({'error': 'Not authorised'}), 403)


@auth.get_password
def get_password(username):
    if username == 'test':
        return 'pass'
    return None
