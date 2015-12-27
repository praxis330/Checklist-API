import unittest
from redis import Redis
from ..profiles.models import ProfileManager


class ProfileManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.redis = Redis()
        self.profile_manager = ProfileManager(db=self.redis)

    def test_should_create_a_profile(self):
        profile = {
            'lists': ['test', 'checklist']
        }
        self.profile_manager.create('test', profile)
        db_profile = self.redis.lrange('profile:test', 0, -1)
        self.assertIn('test', db_profile)
        self.assertIn('checklist', db_profile)

    def tearDown(self):
        self.redis.delete('profile:test')


if __name__ == '__main__':
    unittest.main()
