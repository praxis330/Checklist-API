from app import app, redis_db
from flask.ext.httpauth import HTTPBasicAuth
from flask import jsonify, abort, make_response, request, url_for
import sys

auth = HTTPBasicAuth()

#--------#
# ROUTES #
#--------#

@app.route('/api/checklist/tasks', methods=['GET'])
@auth.login_required
def get_tasks():
	tasks = {}
	for task_id in get_index("tasks:ids"):
		task = get(int(task_id))
		tasks[task_id] = task
	return jsonify(tasks)

@app.route('/api/checklist/tasks/<int:task_id>', methods=['GET'])
@auth.login_required
def get_task(task_id):
	task = {}
	task[task_id] = get(task_id)
	if len(task) == 0:
		abort(404)
	return jsonify(task)

@app.route('/api/checklist/tasks/<int:task_id>', methods=['PUT'])
@auth.login_required
def update_task(task_id):
	if not is_valid(request):
		abort(400)
	if not get(task_id):
		abort(404)

	task = get(task_id)

	for key in task:
		if key in request.json:
			task[key] = request.json[key]
	update(task_id, task)
	return jsonify({task_id: task})

@app.route('/api/checklist/tasks/', methods=['POST'])
@auth.login_required
def create_task():
	if not is_valid(request):
		abort(400)
	task = {
		'name': request.json['name'],
		'done': request.json.get('done', False)
	}
	created, id_num = create(task)
	if created:
		index_add("tasks", id_num)
		return jsonify({id_num: task}), 201
	else:
		abort(500)

@app.route('/api/checklist/tasks/<int:task_id>', methods=['DELETE'])
@auth.login_required
def delete_task(task_id):
	deleted = delete(task_id)
	if deleted:
		return jsonify({'result': True}), 200
	else:
		abort(404)

#--------------#
# DATABASE API #
#--------------#

def create(task):
	id_num = int(redis_db.get("tasks:counter")) + 1
	redis_db.hmset("tasks:%d" % id_num, task)
	
	if redis_db.exists("tasks:%d" % id_num):
		redis_db.incr("tasks:counter")
		index_add("tasks", id_num)
		return (True, id_num)
	return (False, None)

def get(task_id):
	task = redis_db.hgetall("tasks:%d" % task_id)
	return parse_bool(task)

def delete(task_id):
	task_id = "tasks:%d" % task_id
	
	if redis_db.exists(task_id):
		redis_db.delete(task_id)
		index_remove("tasks", task_id)
		return True
	return False

def update(task_id, task):
	redis_db.hmset("tasks:%d" % task_id, task)

def get_index(name):
	return redis_db.smembers(name)

def index_add(name, task_id):
	redis_db.sadd("%s:ids" % name, task_id)

def index_remove(name, task_id):
	redis_db.srem("%s:ids" % name, task_id)

def parse_bool(task):
	if task['done'] == 'True':
		task['done'] = True
	else:
		task['done'] = False
	return task

#----------------#
# ERROR HANDLING #
#----------------#

@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(400)
def bad_request(error):
	return make_response(jsonify({'error': 'Bad request'}), 400)

@app.errorhandler(500)
def internal_error(error):
	return make_response(jsonify({'error': 'Internal server error'}), 500)

@auth.error_handler
def unauthorised():
	return make_response(jsonify({'error': 'Not authorised'}), 403)

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

@auth.get_password
def get_password(username):
	if username == app.config['USERNAME']:
		return app.config['PASSWORD']
	return None