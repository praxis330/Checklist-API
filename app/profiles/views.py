from flask.ext.classy import FlaskView, route
from flask import jsonify, request
from ..core import auth, profile_manager, profile_validator
from ..exceptions import DoesNotExist


class ProfilesView(FlaskView):
    route_prefix = '/api/profile'
    route_base = '/'

    @auth.login_required
    def before_request(self, *args, **kwargs):
        pass

    def before_get(self, profile_name):
        if not profile_manager.exists(profile_name):
            raise DoesNotExist("Profile '%s' does not exist." % profile_name)

    @route('/<profile_name>', methods=['GET'])
    def get(self, profile_name):
        profile_lists = profile_manager.get(profile_name)
        return jsonify({'lists': profile_lists}), 200

    def before_post(self, profile_name):
        profile_validator.validate(request.json, required_fields=['lists'])

    @route('/<profile_name>', methods=['POST'])
    def post(self, profile_name):
        profile_manager.create(profile_name, request.json)
        lists = profile_manager.get(profile_name)
        return jsonify({'lists': lists}), 201

    def before_patch(self, profile_name):
        profile_validator.validate(request.json, required_fields=['lists'])
        if not profile_manager.exists(profile_name):
            raise DoesNotExist("Profile '%s' does not exist." % profile_name)

    @route('/<profile_name>', methods=['PATCH', 'PUT'])
    def patch(self, profile_name):
        profile_manager.update(profile_name, request.json)
        lists = profile_manager.get(profile_name)
        return jsonify({'lists': lists}), 200

    def before_delete(self, profile_name):
        if not profile_manager.exists(profile_name):
            raise DoesNotExist("Profile '%s' does not exist." % profile_name)

    @route('/<profile_name>', methods=['DELETE'])
    def delete(self, profile_name):
        profile_manager.delete(profile_name)
        return jsonify({'success': True}), 204
