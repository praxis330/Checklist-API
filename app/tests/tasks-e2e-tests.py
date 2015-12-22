from app.factory import create_app
from app.core import task_manager
import unittest
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
        self.test_1 = task_manager.create('test', task_1)
        task_2 = {
            "name": "dummy task 2",
            "done": True
        }
        self.test_2 = task_manager.create('test', task_2)

    def tearDown(self):
        task_manager.delete('test', self.test_1)
        task_manager.delete('test', self.test_2)

    def _get_id(self, response):
        obj = json.loads(response.data)
        return int(obj.keys().pop())


class GetListTest(ChecklistTestCase):
    def test_get(self):
        response = self.app.get('/api/checklist/test',
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Basic dGVzdDpwYXNz'
            })
        self.assertEqual(response.status_code, 200)
        self.assertIn(str(self.test_1), response.data)
        self.assertIn(str(self.test_2), response.data)

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
        response = self.app.get('/api/checklist/test/%s' % self.test_2,
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Basic dGVzdDpwYXNz'
            })
        self.assertEqual(response.status_code, 200)
        self.assertIn("%s" % self.test_2, response.data)

    def test_get_nonexistent_item(self):
        response = self.app.get('/api/checklist/test/150',
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Basic dGVzdDpwYXNz'
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
        response = self.app.put('/api/checklist/test/%s' % self.test_1,
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Basic dGVzdDpwYXNz'
            },
            data=json.dumps(data)
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn(str(self.test_1), response.data)
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
        self.assertIn("done field is not of type bool", response.data)

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
        self.assertIn("does not exist", response.data)

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
    def setUp(self):
        super(PostTest, self).setUp()
        self.test_3 = None
        self.new_list_1 = None
        self.new_list_2 = None

    def test_post_item(self):
        data = {'done': True, 'name': 'item 3'}
        response = self.app.post('/api/checklist/test/',
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Basic dGVzdDpwYXNz'
            },
            data=json.dumps(data)
            )
        self.test_3 = self._get_id(response)
        self.assertEqual(response.status_code, 201)
        self.assertIn(str(self.test_3), response.data)
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
        self.new_list_1 = self._get_id(response)
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
        self.new_list_2 = self._get_id(response)
        self.assertEqual(response.status_code, 201)
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
        self.assertIn('name field is required', response.data)

    def tearDown(self):
        super(PostTest, self).tearDown()
        task_manager.delete('test', self.test_3)
        task_manager.delete('new_list', self.new_list_1)
        task_manager.delete('new_list', self.new_list_2)

class DeleteTest(ChecklistTestCase):
    def setUp(self):
        super(DeleteTest, self).setUp()

    def test_delete(self):
        response = self.app.delete('/api/checklist/test/%s' % self.test_2,
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Basic dGVzdDpwYXNz'
            })
        self.assertEqual(response.status_code, 204)

    def test_delete_without_auth(self):
        response = self.app.delete('/api/checklist/test/%s' % self.test_1,
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Basic bla'
            })
        self.assertEqual(response.status_code, 403)
        self.assertIn('Not authorised', response.data)

    def test_delete_nonexistent(self):
        response = self.app.delete('/api/checklist/test/150',
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Basic dGVzdDpwYXNz'
            })
        self.assertEqual(response.status_code, 404)
        self.assertIn('does not exist', response.data)

if __name__ == "__main__":
    unittest.main()
