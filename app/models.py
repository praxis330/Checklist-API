from .exceptions import ValidationError


class IndexManager():
    def __init__(self, db):
        self.db = db

    def get(self, list_name):
        return self.db.smembers("%s:ids" % list_name)

    def add(self, list_name, id_number):
        self.db.sadd("%s:ids" % list_name, id_number)

    def remove(self, list_name, id_number):
        self.db.srem("%s:ids" % list_name, id_number)


class Validator():
    def __init__(self):
        self.model = {}

    def validate(self, obj, required_fields=[]):
        for field_name, field_type in self.model.iteritems():
            try:
                self._validate_type(obj[field_name], field_name, field_type)
            except KeyError:
                self._validate_required_fields(field_name, required_fields)

    def _validate_type(self, field, field_name, field_type):
        if not isinstance(field, field_type):
            raise ValidationError('%s field is not of type %s' %
                (field_name, field_type.__name__)
            )

    def _validate_required_fields(self, field_name, required_fields):
        if field_name in required_fields:
            raise ValidationError('%s field is required' % field_name)


class TaskValidator(Validator):
    def __init__(self):
        self.model = {
            'name': unicode,
            'done': bool,
        }


class ProfileValidator(Validator):
    def __init__(self):
        self.model = {
            'lists': list
        }
