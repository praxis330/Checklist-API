from flask import jsonify, abort, make_response, request
from flask.ext.classy import FlaskView, route
from .core import task_manager, task_validator, auth

class ReadUpdateDeleteMixin(FlaskView):
  def before_request():
    if not task_manager.exists(list_name, id_number):
      abort(404)

  @route('/<list_name>/<int:id_number>', methods=['GET'])
  def get(self, list_name, id_number):
    task = task_manager.get(list_name, id_number)
    return jsonify({id_number: list_name})

  @route('/<list_name>/<int:id_number>', methods=['PATCH'])
  def patch(self, list_name, id_number):
    task_manager.update(list_name, id_number, request.json)
    updated_task = task_manager.get(list_name, id_number)
    return jsonify({id_number: updated_task}) 

  @route('/<list_name>/<int:id_number>', methods=['DELETE'])
  def delete(self, list_name, id_number):
    task_manager.delete(list_name, id_number)
    return jsonify({"success": True}), 204


class ListCreateMixin(FlaskView):
  @route('/<list_name>', methods=['GET'])
  def get_list(self, list_name):
    tasks = task_manager.all(list_name)
    return jsonify(tasks)

  @route('/<list_name>/', methods=['POST'])
  def post(self, list_name):
    task = {
      'name': request.json['name'],
      'done': request.json.get('done', False) # This shouldn't be here.
    }
    id_number = int(task_manager.create(list_name, task))
    return jsonify({id_number: task}), 201


class TasksView(ReadUpdateDeleteMixin, ListCreateMixin):
  route_prefix = '/api/checklist/'
  route_base = '/'
  decorators = [auth.login_required]
