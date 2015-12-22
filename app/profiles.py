from flask.ext.classy import FlaskView, route
from flask import jsonify, request
from .core import auth, profile_manager


class ProfilesView(FlaskView):
    route_prefix = '/api/profile'
    route_base = '/'

    @auth.login_required
    def before_request(self, *args, **kwargs):
        pass

    @route('/<profile_name>/', methods=['POST'])
    def post(self, profile_name):
        profile_manager.create(profile_name, request.json)
        lists = profile_manager.get(profile_name)
        return jsonify({'lists': lists}), 201
