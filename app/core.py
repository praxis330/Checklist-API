from flask import abort, make_response, request
from flask.ext.httpauth import HTTPBasicAuth
from flask_redis import Redis
from functools import wraps
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

# def json_required(endpoint_function):
#   @wraps(endpoint_function)
#   def function_wrapper(list_name, id_number):
#     if not request.json:
#       abort(415)
#     return endpoint_function(list_name, id_number)
#   return function_wrapper

# def validate_inputs(required_fields=[]):
#   def validation_decorator(endpoint_function):
#     @wraps(endpoint_function)
#     def function_wrapper(list_name, id_number):
#       try:
#         task_validator.validate(request.json, required_fields)
#         return endpoint_function(list_name, id_number)
#       except Exception as e:
#         make_response(jsonify({'error': e}), 400)
#     return function_wrapper
#   return validation_decorator
