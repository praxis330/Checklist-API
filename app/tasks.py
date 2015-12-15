from flask import jsonify, request
from flask.ext.classy import FlaskView, route
from .core import task_manager, task_validator, auth


class TasksView(FlaskView):
    route_prefix = '/api/checklist/'
    route_base = '/'

    @auth.login_required
    def before_request(self, *args, **kwargs):
        pass

    def before_get(self, list_name, id_number):
        task_manager.exists(list_name, id_number)

    @route('/<list_name>/<int:id_number>', methods=['GET'])
    def get(self, list_name, id_number):
        task = task_manager.get(list_name, id_number)
        return jsonify({id_number: task})

    def before_patch(self, list_name, id_number):
        task_validator.validate(request.json, required_fields=[])
        task_manager.exists(list_name, id_number)

    @route('/<list_name>/<int:id_number>', methods=['PATCH'])
    def patch(self, list_name, id_number):
        task_manager.update(list_name, id_number, request.json)
        updated_task = task_manager.get(list_name, id_number)
        return jsonify({id_number: updated_task})

    def before_delete(self, list_name, id_number):
        task_manager.exists(list_name, id_number)

    @route('/<list_name>/<int:id_number>', methods=['DELETE'])
    def delete(self, list_name, id_number):
        task_manager.delete(list_name, id_number)
        return jsonify({"success": True}), 204

    @route('/<list_name>', methods=['GET'])
    def get_list(self, list_name):
        tasks = task_manager.all(list_name)
        return jsonify(tasks)

    def before_post(self, list_name):
        task_validator.validate(request.json, required_fields=['name'])

    @route('/<list_name>/', methods=['POST'])
    def post(self, list_name):
        id_number = int(task_manager.create(list_name, request.json))
        task = task_manager.get(list_name, id_number)
        return jsonify({id_number: task}), 201
