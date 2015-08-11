from flask import Flask, jsonify, abort, make_response, request, url_for
from flask.ext.httpauth import HTTPBasicAuth
import os

auth = HTTPBasicAuth()
USERNAME = os.environ.get('USER')
PASSWORD = os.environ.get('PASSWORD')

tasks = [
	{
		'id': 1,
		'name': u'Finish android app',
		'done': False,
	},
	{
		'id': 2,
		'name': u'Code API endpoints',
		'done': False,
	}
]

#--------#
# ROUTES #
#--------#

@app.route('/api/checklist/tasks', methods=['GET'])
@auth.login_required
def get_tasks():
	return jsonify({'tasks': [get_uri(task, 'get_task') for task in tasks]})

@app.route('/api/checklist/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
	task = [task for task in tasks if task['id'] == task_id]
	if len(task) == 0:
		abort(404)
	return jsonify({'tasks': task[0]})

@app.route('/api/checklist/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
	task = [task for task in tasks if task['id'] == task_id]
	if len(task) == 0:
		abort(404)
	if not is_valid(request):
		abort(400)
	task[0]['title'] = request.json.get('name', task[0]['title'])
	task[0]['done'] = request.json.get('done', task[0]['done'])
	return jsonify({'task': task[0]})

@app.route('/api/checklist/tasks/', methods=['POST'])
def create_task():
	if not is_valid(request):
		abort(400)
	task = {
		'id': tasks[-1]['id'] + 1,
		'name': request.json['name'],
		'done': request.json.get('done', False)
	}
	tasks.append(task)
	return jsonify({'task': task}), 201

@app.route('/api/checklist/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
	task = [task for task in tasks if task['id'] == task_id]
	if len(task) == 0:
		abort(404)
	tasks.remove(task[0])
	return jsonify({'result': True}), 200

#------------------#
# HELPER FUNCTIONS #
#------------------#

def is_valid(request):
	flag = True
	if not request.json:
		flag = False
	if 'name' in request.json and type(request.json['name']) != unicode:
		flag = False
	if 'done' in request.json and type(request.json['done']) is not bool:
		flag = False
	return flag

def get_uri(task, endpoint):
	new_task = {}
	for field in task:
		if field == 'id':
			new_task['uri'] = url_for(endpoint, task_id=task['id'], _external=True)
		else:
			new_task[field] = task[field]
	return new_task

@auth.get_password
def get_password(username):
	if username == USERNAME:
		return PASSWORD
	return None

#----------------#
# ERROR HANDLING #
#----------------#

@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(404)
def bad_request(error):
	return make_response(jsonify({'error': 'Bad request'}), 400)

@auth.error_handler
def unauthorised():
	return make_response(jsonify({'error': 'Not authorised'}), 403)