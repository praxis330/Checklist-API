class Validator():
  def __init__(self):
    self.model = {}

  def validate(self, task, required_fields=[]):
    for field_name, field_type in self.model.iteritems():
      try:
        self._validate_type(task[field_name], field_type)
      except KeyError:
        self._validate_required_fields(field_name, required_fields)

  def _validate_type(self, field, field_type):
    if not isinstance(field, field_type):
      raise Exception('%s field is not of type %s' % field_name, field_type)

  def _validate_required_fields(self, field_name, required_fields):
    if field_name in required_fields:
      raise Exception('%s field is required' % field_name)


class TaskValidator(Validator):
  def __init__(self):
    self.model = {
      'name': unicode,
      'done': bool,
    }


class TaskManager():
  def __init__(self, db, index):
    self.db = db
    self.index = index

  def all(self, list_name):
    objects = {}
    for id_number in self.index.get(list_name):
      task = self.get(list_name, id_number)
      objects[id_number] = task
    return objects

  def create(self, list_name, request_json):
    id_number = self._get_id_number(list_name)
    task_id = self._parse_id(list_name, id_number)
    task = self._parse_new_task(request_json)
    self.db.hmset(task_id, task)
    self.index.add(list_name, id_number)
    return id_number

  def get(self, list_name, id_number):
    task_id = self._parse_id(list_name, id_number)
    task = self.db.hgetall(task_id)
    return self.serialise(task)

  def update(self, list_name, id_number, new_data):
    old_task = self.get(list_name, id_number)
    updated_task = self._parse_updated_task(old_task, new_data)
    task_id = self._parse_id(list_name, id_number)
    self.db.hmset(task_id, updated_task)
    return updated_task

  def delete(self, list_name, id_number):
    task_id = self._parse_id(list_name, id_number)
    self.db.delete(task_id)
    self.index.remove(list_name, id_number)

  def exists(self, list_name, id_number):
    task_id = self._parse_id(list_name, id_number)
    return True if self.db.exists(task_id) else False

  def serialise(self, task):
    if 'done' in task:
      return self._parse_bool(task)
    else:
      return task

  def _parse_bool(self, task):
    if task['done'] == 'True':
      task['done'] = True
    elif task['done'] == 'False':
      task['done'] = False
    return task

  def _parse_id(self, list_name, id_number):
    return "%(list_name)s:%(id_number)s" % {
      "list_name": list_name,
      "id_number": id_number
    }

  def _get_id_number(self, list_name):
    counter_name = "%s:counter" % list_name
    self.db.incr(counter_name)
    return self.db.get(counter_name)

  def _parse_new_task(self, new_data):
    task = dict()
    task['name'] = new_data['name']
    task['done'] = new_data.get('done', False)
    return task

  def _parse_updated_task(self, old_task, new_data):
    updated_task = dict()
    for key in old_task:
      try:
        updated_task[key] = new_data[key]
      except KeyError:
        updated_task[key] = old_task[key]
    return updated_task


class IndexManager():
  def __init__(self, db):
    self.db = db

  def get(self, list_name):
    return self.db.smembers("%s:ids" % list_name)

  def add(self, list_name, id_number):
    self.db.sadd("%s:ids" % list_name, id_number)

  def remove(self, list_name, id_number):
    self.db.srem("%s:ids" % list_name, id_number)
