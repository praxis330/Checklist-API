from flask import make_response, jsonify


def not_found(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def bad_request(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def internal_error(error):
    return make_response(jsonify({"error": "Internal server error"}))
