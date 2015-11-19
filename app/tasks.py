from flask import Blueprint, jsonify, abort, make_response, request, url_for
from flask.ext.httpauth import HTTPBasicAuth
from .core import task_manager, task_validator, json_required, validate_inputs
import sys

auth = HTTPBasicAuth()
tasks = Blueprint('tasks', __name__)

@tasks.route('/api/checklist/<list_name>', methods=['GET'])
@auth.login_required
@json_required
def get_tasks(list_name):
	tasks = task_manager.all(list_name)
	return jsonify(tasks)

@tasks.route('/api/checklist/<list_name>/<int:id_number>', methods=['GET'])
@auth.login_required
@json_required
def get_task(list_name, id_number):
	if task_manager.exists(list_name, id_number):
		task = task_manager.get(list_name, id_number)
		response = dict(id_number, task) 
		return jsonify(response)
	else:
		abort(404)

@tasks.route('/api/checklist/<list_name>/<int:id_number>', methods=['PUT'])
@auth.login_required
@json_required
@validate_inputs
def update_task(list_name, id_number):
  if task_manager.exists(list_name, id_number):
    task_manager.update(list_name, id_number, request.json)
    updated_task = task_manager.get(list_name, id_number)
    return jsonify({id_number, updated_task})
  else:
    return abort(404)		

@tasks.route('/api/checklist/<name>/', methods=['POST'])
@auth.login_required
@json_required
@validate_inputs(required_fields=['name'])
def create_task(name):
 	task = {
 		'name': request.json['name'],
 		'done': request.json.get('done', False)
 	}
 	id_num = task_manager.create(name, task)
 	return jsonify({id_num: task}), 201

@tasks.route('/api/checklist/<name>/<int:item_id>', methods=['DELETE'])
@auth.login_required
@json_required
def delete_task(name, item_id):
  if not task_manager.exists(list_name, id_number):
    abort(404)
  task_manager.delete(list_name, id_number)
  return jsonify({success: True}}, 204

#----------------#
# ERROR HANDLING #
#----------------#

@tasks.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'Not found'}), 404)

@tasks.errorhandler(400)
def bad_request(error):
	return make_response(jsonify({'error': 'Bad request'}), 400)

@tasks.errorhandler(415)
def unsupported_media_type(error):
  return make_response(jsonify({'error': 'No JSON in request'})

# @app.errorhandler(500)
# def internal_error(error):
# 	return make_response(jsonify({'error': 'Internal server error'}), 500)

@auth.error_handler
def unauthorised():
	return make_response(jsonify({'error': 'Not authorised'}), 403)

@auth.get_password
def get_password(username):
	if username == 'test':
		return 'pass'
	return None
