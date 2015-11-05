from flask import Blueprint, jsonify, abort, make_response, request, url_for
from flask.ext.httpauth import HTTPBasicAuth
import sys

auth = HTTPBasicAuth()
tasks = Blueprint('tasks', __name__)

#--------#
# ROUTES #
#--------#

@tasks.route('/api/checklist/<name>', methods=['GET'])
@auth.login_required
def get_tasks(name):
	tasks = {}
	for item_id in get_index("%s:ids" % name):
		task = get(name, int(item_id))
		tasks[item_id] = task
	return jsonify(tasks)

@tasks.route('/api/checklist/<name>/<int:item_id>', methods=['GET'])
@auth.login_required
def get_task(name, item_id):
	task_dict = {}
	task = get(name, item_id)
	if len(task) != 0:
		task_dict[item_id] = task
		return jsonify(task_dict)
	else:
		abort(404)

@tasks.route('/api/checklist/<name>/<int:item_id>', methods=['PUT'])
@auth.login_required
def update_task(name,item_id):
	if not is_valid_task(request):
		abort(400)
	
	task = get(name, item_id)
	if len(task) != 0:
		for key in task:
			if key in request.json:
				task[key] = request.json[key]
		update(name, item_id, task)
		return jsonify({item_id: task})
	else:
		abort(404)
		

@tasks.route('/api/checklist/<name>/', methods=['POST'])
@auth.login_required
def create_task(name):
	if not is_valid_task(request) or 'name' not in request.json:
		abort(400)
	task = {
		'name': request.json['name'],
		'done': request.json.get('done', False)
	}
	id_num = create(name, task)
	index_add("tasks", id_num)
	return jsonify({id_num: task}), 201

@tasks.route('/api/checklist/<name>/<int:item_id>', methods=['DELETE'])
@auth.login_required
def delete_task(name, item_id):
	deleted = delete(name, item_id)
	if deleted:
		return jsonify({'result': True}), 200
	else:
		abort(404)

@tasks.route('/api/checklist/profiles/<name>', methods=['GET'])
@auth.login_required
def get_profile(name):
	profile = get_profile(name)
	return jsonify(profile), 200

@tasks.route('/api/checklist/profiles/<name>/', methods=['POST','PUT', 'DELETE'])
@auth.login_required
def update_profile(name):
	if request.method == 'POST':
		try:
			if is_valid_profile(request):
				profile_primary = request.json.get('primary', '')
				profile_secondary = request.json.get('secondary', [])
				profile = create_profile(name, profile_primary, profile_secondary)
				return jsonify(profile), 200
		except Exception as e:
			return make_response(jsonify({'error': '%s' % e}), 400)
	else:
		pass


#----------------------#
# DATABASE API - TASKS #
#----------------------#

def create(name, task):
	counter = redis_db.get("%s:counter" % name)
	if counter:
		item_id = int(redis_db.get("%s:counter" % name)) + 1
	else:
		redis_db.set("%s:counter" % name, 0)
		item_id = 1
	task_id = "%s:%d" % (name, item_id)
	redis_db.hmset(task_id, task)
	redis_db.incr("%s:counter" % name)
	index_add(name, item_id)
	return item_id

def get(name, item_id):
	task_id = "%s:%s" % (name, item_id)
	task = redis_db.hgetall(task_id)
	if 'done' in task:
		return parse_bool(task)
	else:
		return task

def delete(name, item_id):
	task_id = "%s:%d" % (name, item_id)	
	if redis_db.exists(task_id):
		redis_db.delete(task_id)
		index_remove(name, item_id)
		return True
	return False

def update(name, item_id, task):
	task_id = "%s:%d" % (name, item_id)
	redis_db.hmset(task_id, task)

def parse_bool(task):
	if task['done'] == 'True':
		task['done'] = True
	elif task['done'] == 'False':
		task['done'] = False
	return task

#------------------------#
# DATABASE API - INDEXES #
#------------------------#

def get_index(name):
	return redis_db.smembers(name)

def index_add(name, item_id):
	redis_db.sadd("%s:ids" % name, item_id)

def index_remove(name, item_id):
	redis_db.srem("%s:ids" % name, item_id)

#-------------------------#
# DATABASE API - PROFILES #
#-------------------------#

def create_profile(name, primary_list, secondary_lists):
	create_primary_list(name, primary_list)
	create_secondary_lists(name, secondary_lists)
	return {'primary':primary_list, 'secondary':secondary_lists}

def get_primary_list(name):
	return redis_db.get("%s:profile:primary" % name)

def create_primary_list(name, primary_list):
	redis_db.set("%s:profile:primary" % name, primary_list)

def get_secondary_lists(name):
	rset = redis_db.smembers("%s:profile:secondary" % name)
	return [item for item in rset]

def create_secondary_lists(name, secondary_lists):
	redis_db.sadd("%s:profile:secondary" % name, *secondary_lists)

def get_profile(name):
	primary = get_primary_list(name)
	secondary = get_secondary_lists(name)
	return {'primary': primary, 'secondary': secondary}

#----------------#
# ERROR HANDLING #
#----------------#

@tasks.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'Not found'}), 404)

@tasks.errorhandler(400)
def bad_request(error):
	return make_response(jsonify({'error': 'Bad request'}), 400)

# @app.errorhandler(500)
# def internal_error(error):
# 	return make_response(jsonify({'error': 'Internal server error'}), 500)

@auth.error_handler
def unauthorised():
	return make_response(jsonify({'error': 'Not authorised'}), 403)

#------------------#
# HELPER FUNCTIONS #
#------------------#

def is_valid_task(request):
	flag = True
	if not request.json:
		flag = False
	if 'name' in request.json and type(request.json['name']) != unicode:
		flag = False
	if 'done' in request.json and type(request.json['done']) is not bool:
		flag = False
	return flag

def is_valid_profile(request):
	if not request.json:
		raise Exception('Request is not JSON formatted')
	fields = ['primary', 'secondary']
	for field in fields:
		if field not in request.json:
			raise Exception('Request does not include a "%s" field.' % field)
	return True

@auth.get_password
def get_password(username):
	if username == 'test':
		return 'pass'
	return None