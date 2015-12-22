import unittest
from ..factory import create_app


class ProfileTestCase(unittest.TestCase):
    def setUp(self):
        app = create_app()
        self.app = app.test_client()


class PostTest(ProfileTestCase):
    def test_post(self):
        response = self.app.get('/api/profile/test/')

if __name__ == '__main__':
    unittest.main()
