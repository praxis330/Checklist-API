from app.factory import create_app
from app.core import task_manager
import unittest
import os
import json


class ChecklistTestCase(unittest.TestCase):
  """
  Base class for testing app. Sets up simple fixtures in the redis server
  to be removed at the end of a test.
  """
  def setUp(self):
    # set up first item
    app = create_app()
    self.app = app.test_client()
    task_1 = {
      "name": "dummy task",
      "done": False
    }
    task_manager.create('test', task_1)
    task_2 = {
      "name": "dummy task 2",
      "done": True
    }
    task_manager.create('test', task_2)
  
  def tearDown(self):
    task_manager.delete('test', 1)
    task_manager.delete('test', 2)

class GetListTest(ChecklistTestCase):
  def test_get(self):
    response = self.app.get('/api/checklist/test',
      headers={
        'Content-Type': 'application/json',
        'Authorization': 'Basic Y2NvcmRlbmllcjpwYXNz'
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
        'Authorization': 'Basic Y2NvcmRlbmllcjpwYXNz'
      })
    self.assertEqual(response.status_code, 200)
    self.assertIn("1", response.data)

  def test_get_nonexistent_item(self):
    response = self.app.get('/api/checklist/test/2',
      headers={
        'Content-Type': 'application/json',
        'Authorization': 'Basic Y2NvcmRlbmllcjpwYXNz'
      })
    self.assertEqual(response.status_code, 404)
    self.assertIn("does not exist", response.data)

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
        'Authorization': 'Basic Y2NvcmRlbmllcjpwYXNz'
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
        'Authorization': 'Basic Y2NvcmRlbmllcjpwYXNz'
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
        'Authorization': 'Basic Y2NvcmRlbmllcjpwYXNz'
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
        'Authorization': 'Basic Y2NvcmRlbmllcjpwYXNz'
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
        'Authorization': 'Basic Y2NvcmRlbmllcjpwYXNz'
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
        'Authorization': 'Basic Y2NvcmRlbmllcjpwYXNz'
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
        'Authorization': 'Basic Y2NvcmRlbmllcjpwYXNz'
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

if __name__ == "__main__":
  unittest.main()