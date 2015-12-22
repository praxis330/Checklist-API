import unittest
import json
from app.factory import create_app


class ProfileTestCase(unittest.TestCase):
    def setUp(self):
        app = create_app()
        self.app = app.test_client()


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


if __name__ == '__main__':
    unittest.main()
