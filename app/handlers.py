from flask import make_response, jsonify

def not_found(error):
  return make_response(jsonify({"error": "Not found"}))

def bad_request(error):
  return make_response(jsonify({"error": "Bad request"}))

def internal_error(error):
  return make_response(jsonify({"error": "Internal server error"}))