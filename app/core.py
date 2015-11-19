from flask_redis import Redis
from .models import TaskManager, IndexManager

redis = Redis()
index_manager = IndexManager(db=redis)
task_manager = TaskManager(db=redis, index=index_manager)
task_validator = TaskValidator()

def json_required(endpoint_function):
  def function_wrapper(list_name, id_number):
    if not request.json:
      abort(415)
    return endpoint_function(list_name, id_number)
  return function_wrapper

def validate_inputs(required_fields=[]):
  def validation_decorator(endpoint_function):
    def function_wrapper(list_name, id_number):
      try:
        task_validator.validate(request.json, required_fields)
        return endpoint_function(list_name, id_number)
      except Exception as e:
        make_response(jsonify({'error': e}), 400
    return function_wrapper
  return validation_decorator
