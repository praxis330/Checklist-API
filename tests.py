from app import *
import os
import json
import unittest

class AppTestCase(unittest.TestCase):
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
    redis_db.sadd("test:ids", "test:1", "test:2")
    # set up counter
    redis_db.set("test:counter", 2)
    # set up app
    self.app = app.test_client()

  def tearDown(self):
    redis_db.delete("test:1", "test:2")
    redis_db.srem("test:ids", "test:1", "test:2")

class GetTest(AppTestCase):
  def test_get(self):
    response = self.app.get('/api/checklist/test',
      headers={
        'Content-Type': 'application/json',
        'Authorization': 'Basic dGVzdDpwYXNz'
      })
    self.assertEqual(response.status_code, 200)
    self.assertIn("test:1", response.data)
    self.assertIn("test:2", response.data)

  def test_get_without_auth(self):
    response = self.app.get('/api/checklist/test',
      headers={
        'Content-Type': 'application/json',
        'Authorization': 'Basic bla'
      })
    self.assertEqual(response.status_code, 403)
    self.assertIn("Not authorised", response.data)

class GetItemTest(AppTestCase):
  def test_get_item(self):
    response = self.app.get('/api/checklist/test/1',
      headers={
        'Content-Type': 'application/json',
        'Authorization': 'Basic dGVzdDpwYXNz'
      })
    self.assertEqual(response.status_code, 200)
    self.assertIn("test:1", response.data)

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

class PutTest(AppTestCase):
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
    self.assertIn('test:1', response.data)
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

class PostTest(AppTestCase):
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
    self.assertIn('test:3', response.data)
    self.assertIn('item 3', response.data)

  def test_post_first_item(self):
    data = {'done': True, 'name': 'first item'}
    response = self.app.post('/api/checklist/new_list/',
      headers={
        'Content-Type': 'application/json',
        'Authorization': 'Basic dGVzdDpwYXNz'
      },
      data=json.dumps(data)
    )
    self.assertEqual(response.status_code, 201)
    self.assertIn('new_list:1', response.data)
    self.assertIn('first item', response.data)

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

class DeleteTest(AppTestCase):
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

if __name__ == "__main__":
  unittest.main()