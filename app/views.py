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
	tasks = []
	tasks_number = int(redis_db.get("tasks:counter"))
	for i in range(tasks_number):
		task = get(i + 1)
		task['id'] = i + 1
		tasks.append(task)
	return jsonify({'tasks': tasks})

@app.route('/api/checklist/tasks/<int:task_id>', methods=['GET'])
@auth.login_required
def get_task(task_id):
	task = list(get(task_id))
	if len(task) == 0:
		abort(404)
	return jsonify({'task': task[0]})

@app.route('/api/checklist/tasks/<int:task_id>', methods=['PUT'])
@auth.login_required
def update_task(task_id):
	old_task = task = get(task_id)
	print >>sys.stderr, old_task

	if not is_valid(request):
		abort(400)
	if len(old_task) == 0:
		abort(404)

	for field in ['name', 'done']:
		if request.json[field]:
			task[field] = request.json[field]
	update(task_id, task)
	return jsonify({'task': task})

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
	print >>sys.stderr, created
	if created:
		task['id']= id_num
		print >>sys.stderr, task['id']
		return jsonify({'task': task}), 201
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
	redis_db.incr("tasks:counter")
	if redis_db.exists("tasks:%d" % id_num):
		return (True, id_num)
	return (False, None)

def get(task_id):
	task = redis_db.hgetall("tasks:%d" % task_id)
	return task

def delete(task_id):
	task_id = "tasks:%d" % task_id
	task = redis_db.exists(task_id)
	if task:
		redis_db.delete(task_id)
		redis_db.decr("tasks:counter")
		return True
	return False

def update(task_id, task):
	redis_db.hmset("tasks:%d" % task_id, task)

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

# def get_uri(task, endpoint):
# 	new_task = {}
# 	for field in task:
# 		if field == 'id':
# 			new_task['uri'] = url_for(endpoint, task_id=task['id'], _external=True)
# 		else:
# 			new_task[field] = task[field]
# 	return new_task

@auth.get_password
def get_password(username):
	if username == app.config['USERNAME']:
		return app.config['PASSWORD']
	return None