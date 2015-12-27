import unittest
import json
from app.factory import create_app
from ..profiles.models import ProfileManager
from redis import Redis


class ProfileTestCase(unittest.TestCase):
    def setUp(self):
        app = create_app()
        self.app = app.test_client()
        r = Redis()
        self.profile_manager = ProfileManager(db=r)


class GetItemTest(ProfileTestCase):
    def setUp(self):
        super(GetItemTest, self).setUp()
        self.profile_manager.create('test', {'lists': ['checklist', 'test']})

    def test_get(self):
        response = self.app.get('/api/profile/%s' % 'test',
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Basic dGVzdDpwYXNz'
            }
        )
        self.assertEqual(response.status_code, 200)

    def test_get_without_auth(self):
        response = self.app.get('/api/profile/%s' % 'test',
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Basic blabla'
            }
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn('Not authorised', response.data)

    def test_get_nonexistent_item(self):
        response = self.app.get('/api/profile/%s' % 'absent',
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Basic dGVzdDpwYXNz'
            }
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn('does not exist', response.data)


class PostTest(ProfileTestCase):
    def test_post(self):
        data = {'lists': ['test', 'checklist']}
        response = self.app.post('/api/profile/%s/' % 'test',
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Basic dGVzdDpwYXNz'
            },
            data=json.dumps(data)
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn('checklist', response.data)

    def test_post_without_auth(self):
        data = {'lists': ['test', 'checklist']}
        response = self.app.post('/api/profile/%s/' % 'test',
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Basic blabla'
            },
            data=json.dumps(data)
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn('Not authorised', response.data)

    def test_post_invalid_request(self):
        data = {'listo': 'not a list'}
        response = self.app.post('api/profile/%s/' % 'test',
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Basic dGVzdDpwYXNz'
            },
            data=json.dumps(data)
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('lists field is required', response.data)

    def tearDown(self):
        self.profile_manager.delete('test')

class PatchTest(ProfileTestCase):
    def setUp(self):
        super(PatchTest, self).setUp()
        self.profile_manager.create('test', {'lists': ['checklist', 'test']})

    def test_patch(self):
        data = {'lists': ['test', 'another_list']}
        response = self.app.put('api/profile/%s/' % 'test',
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Basic dGVzdDpwYXNz'
            },
            data=json.dumps(data)
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('another_list', response.data)

    def test_without_auth(self):
        data = {'lists': ['test', 'another_list']}
        response = self.app.put('api/profile/%s/' % 'test',
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Basic blabla'
            },
            data=json.dumps(data)
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn('Not authorised', response.data)

    def test_post_invalid_request(self):
        data = {'listo': ['test', 'another_list']}
        response = self.app.put('api/profile/%s/' % 'test',
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Basic dGVzdDpwYXNz'
            },
            data=json.dumps(data)
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('lists field is required', response.data)

class DeleteTest(ProfileTestCase):
    def setUp(self):
        super(DeleteTest, self).setUp()
        self.profile_manager.create('test', {'lists': ['checklist', 'test']})

    def test_delete(self):
        response = self.app.delete('api/profile/%s' % 'test',
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Basic dGVzdDpwYXNz'
            }
        )
        self.assertEqual(response.status_code, 204)

    def test_delete_without_auth(self):
        response = self.app.delete('api/profile/%s' % 'test',
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Basic blabla'
            }
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn('Not authorised', response.data)

    def test_delete_non_existent_profile(self):
        response = self.app.delete('api/profile/%s' % 'absent',
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Basic dGVzdDpwYXNz'
            }
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn('does not exist', response.data)


if __name__ == '__main__':
    unittest.main()
