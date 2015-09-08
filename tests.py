from app import *
import os
import json
import unittest
import sys

class ChecklistTestCase(unittest.TestCase):
  """
  Base class for testing app. Sets up simple fixtures in the redis server
  to be removed at the end of a test.
  """
  def setUp(self):
    # set up first item
    task_1 = {
      "name": "dummy task",
      "done": False
    }
    redis_db.hmset("test:1", task_1)
    # set up second item
    task_2 = {
      "name": "dummy task 2",
      "done": True
    }
    redis_db.hmset("test:2", task_2)
    # set up index
    redis_db.sadd("test:ids", "1", "2")
    # set up counter
    redis_db.set("test:counter", 2)
    # set up app
    self.app = app.test_client()

  def tearDown(self):
    redis_db.delete("test:1", "test:2")
    redis_db.srem("test:ids", "1", "2")

class GetListTest(ChecklistTestCase):
  def test_get(self):
    response = self.app.get('/api/checklist/test',
      headers={
        'Content-Type': 'application/json',
        'Authorization': 'Basic dGVzdDpwYXNz'
      })
    self.assertEqual(response.status_code, 200)
    self.assertIn("1", response.data)
    self.assertIn("2", response.data)

  def test_get_without_auth(self):
    response = self.app.get('/api/checklist/test',
      headers={
        'Content-Type': 'application/json',
        'Authorization': 'Basic bla'
      })
    self.assertEqual(response.status_code, 403)
    self.assertIn("Not authorised", response.data)

class GetItemTest(ChecklistTestCase):
  def test_get_item(self):
    response = self.app.get('/api/checklist/test/1',
      headers={
        'Content-Type': 'application/json',
        'Authorization': 'Basic dGVzdDpwYXNz'
      })
    self.assertEqual(response.status_code, 200)
    self.assertIn("1", response.data)

  def test_get_nonexistent_item(self):
    response = self.app.get('/api/checklist/test/150',
      headers={
        'Content-Type': 'application/json',
        'Authorization': 'Basic dGVzdDpwYXNz'
      })
    self.assertEqual(response.status_code, 404)
    self.assertIn("Not found", response.data)

  def test_get_item_without_auth(self):
    response = self.app.get('/api/checklist/test/1',
      headers={
        'Content-Type': 'application/json',
        'Authorization': 'Basic bla'
      })
    self.assertEqual(response.status_code, 403)
    self.assertIn("Not authorised", response.data)

class PutTest(ChecklistTestCase):
  def test_put_item(self):
    data = {'done': True}
    response = self.app.put('/api/checklist/test/1',
      headers={
        'Content-Type': 'application/json',
        'Authorization': 'Basic dGVzdDpwYXNz'
      },
      data=json.dumps(data)
    )
    self.assertEqual(response.status_code, 200)
    self.assertIn('1', response.data)
    self.assertIn('true', response.data)

  def test_put_bad_request(self):
    data = {'done': "true"}
    response = self.app.put('/api/checklist/test/1',
      headers={
        'Content-Type': 'application/json',
        'Authorization': 'Basic dGVzdDpwYXNz'
      },
      data=json.dumps(data)
    )
    self.assertEqual(response.status_code, 400)
    self.assertIn("Bad request", response.data)

  def test_put_nonexistent_item(self):
    data = {'done': True}
    response = self.app.put('/api/checklist/test/150',
      headers={
        'Content-Type': 'application/json',
        'Authorization': 'Basic dGVzdDpwYXNz'
      },
      data=json.dumps(data)
    )
    self.assertEqual(response.status_code, 404)
    self.assertIn("Not found", response.data)

  def test_put_without_auth(self):
    data = {'done': True}
    response = self.app.put('/api/checklist/test/1',
      headers={
        'Content-Type': 'application/json',
        'Authorization': 'Basic bla'
      },
      data=json.dumps(data)
    )
    self.assertEqual(response.status_code, 403)
    self.assertIn("Not authorised", response.data)

class PostTest(ChecklistTestCase):
  def test_post_item(self):
    data = {'done': True, 'name': 'item 3'}
    response = self.app.post('/api/checklist/test/',
      headers={
        'Content-Type': 'application/json',
        'Authorization': 'Basic dGVzdDpwYXNz'
      },
      data=json.dumps(data)
    )
    self.assertEqual(response.status_code, 201)
    self.assertIn('3', response.data)
    self.assertIn('item 3', response.data)

  def test_post_new_items(self):
    data = {'done': True, 'name': 'first item'}
    response = self.app.post('/api/checklist/new_list/',
      headers={
        'Content-Type': 'application/json',
        'Authorization': 'Basic dGVzdDpwYXNz'
      },
      data=json.dumps(data)
    )
    self.assertEqual(response.status_code, 201)
    self.assertIn('1', response.data)
    self.assertIn('first item', response.data)
    # second item
    data = {'done': True, 'name': 'second item'}
    response = self.app.post('/api/checklist/new_list/',
      headers={
        'Content-Type': 'application/json',
        'Authorization': 'Basic dGVzdDpwYXNz'
      },
      data=json.dumps(data)
    )
    self.assertEqual(response.status_code, 201)
    self.assertIn('2', response.data)
    self.assertIn('second item', response.data)

  def test_post_without_auth(self):
    data = {'done': True, 'name': 'item 3'}
    response = self.app.post('/api/checklist/test/',
      headers={
        'Content-Type': 'application/json',
        'Authorization': 'Basic bla'
      },
      data=json.dumps(data)
    )
    self.assertEqual(response.status_code, 403)
    self.assertIn('Not authorised', response.data)

  def test_post_bad_request(self):
    data = {'done': True}
    response = self.app.post('/api/checklist/test/',
      headers={
        'Content-Type': 'application/json',
        'Authorization': 'Basic dGVzdDpwYXNz'
      },
      data=json.dumps(data)
    )
    self.assertEqual(response.status_code, 400)
    self.assertIn('Bad request', response.data)

  def tearDown(self):
    super(PostTest, self).tearDown()
    redis_db.delete('test:3', 'new_list:1')
    redis_db.srem('test:ids', 'test:3')
    redis_db.srem('new_list:ids', 'new_list:1')
    redis_db.set('test:counter', 2)
    redis_db.delete('new_list:counter')

class DeleteTest(ChecklistTestCase):
  def test_delete(self):
    response = self.app.delete('/api/checklist/test/2',
      headers={
        'Content-Type': 'application/json',
        'Authorization': 'Basic dGVzdDpwYXNz'
      }
    )
    self.assertEqual(response.status_code, 200)
    self.assertIn('true', response.data)

  def test_delete_without_auth(self):
    response = self.app.delete('/api/checklist/test/2',
      headers={
        'Content-Type': 'application/json',
        'Authorization': 'Basic bla'
      }
    )
    self.assertEqual(response.status_code, 403)
    self.assertIn('Not authorised', response.data)

  def test_delete_nonexistent(self):
    response = self.app.delete('/api/checklist/test/150',
      headers={
        'Content-Type': 'application/json',
        'Authorization': 'Basic dGVzdDpwYXNz'
      }
    )
    self.assertEqual(response.status_code, 404)
    self.assertIn('Not found', response.data)

class ProfileTestCase(unittest.TestCase):
  def setUp(self):
    profile_primary = 'tasks'
    redis_db.set('test:profile:primary', 'tasks')
    profile_secondary = [
      'not an important list 1',
      'not an important list 2'
    ]
    redis_db.sadd('test:profile:secondary', *profile_secondary)
    self.app = app.test_client()

  def tearDown(self):
    redis_db.delete('test:profile:primary')
    redis_db.delete('test:profile:secondary')

class GetProfileTest(ProfileTestCase):
  def test_get(self):
    response = self.app.get('/api/checklist/profiles/test',
      headers={
        'Content-Type': 'application/json',
        'Authorization': 'Basic dGVzdDpwYXNz'
      }
    )
    self.assertEqual(response.status_code, 200)
    self.assertIn('primary', response.data)
    self.assertIn('secondary', response.data)

  def test_get_without_auth(self):
    response = self.app.get('/api/checklist/profiles/test',
      headers={
        'Content-Type': 'application/json',
        'Authorization': 'Basic bla'
      }
    )
    self.assertEqual(response.status_code, 403)
    self.assertIn('Not authorised', response.data)

class PostProfileTest(ProfileTestCase):
  def test_post(self):
    data = {
      'primary': 'important list',
      'secondary': [
        'less important',
        'even less important'
      ]
    }
    response = self.app.post('/api/checklist/profiles/test/',
      headers={
        'Content-Type': 'application/json',
        'Authorization': 'Basic dGVzdDpwYXNz'
      },
      data=json.dumps(data)
    )
    self.assertEqual(response.status_code, 200)
    self.assertIn('important list', response.data)
    self.assertIn('less important', response.data)
    self.assertIn('even less important', response.data)

  def test_partial_post(self):
    data = {
      'primary': 'important list',
    }
    response = self.app.post('/api/checklist/profiles/test/',
      headers={
        'Content-Type': 'application/json',
        'Authorization': 'Basic dGVzdDpwYXNz'
      },
      data=json.dumps(data)
    )
    self.assertEqual(response.status_code, 400)
    self.assertIn('Request does not include a \\"secondary\\" field.', response.data)

if __name__ == "__main__":
  unittest.main()