import unittest
from redis import Redis
from ..profiles.models import ProfileManager


class ProfileManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.redis = Redis()
        self.profile_manager = ProfileManager(db=self.redis)
        self.test_profile = ['test', 'another_list']
        self.redis.lpush('profile:test', *self.test_profile)

    def test_should_create_a_profile(self):
        profile = {
            'lists': ['test', 'checklist']
        }
        self.profile_manager.create('new_profile', profile)
        db_profile = self.redis.lrange('profile:new_profile', 0, -1)
        self.assertIn('test', db_profile)
        self.assertIn('checklist', db_profile)

    def test_should_get_a_profile(self):
        profile = self.profile_manager.get('test')
        for item in profile:
            self.assertIn(item, self.test_profile)

    def test_should_return_true_if_profile_exits(self):
        exists = self.profile_manager.exists('test')
        self.assertEqual(exists, True)

    def test_should_return_false_if_profile_does_not_exist(self):
        not_exists = self.profile_manager.exists('blabla')
        self.assertEqual(not_exists, False)

    def test_should_update_a_profile(self):
        new_profile = ['list', 'another_list']
        self.profile_manager.update('test', {'lists': new_profile})
        updated_profile = self.profile_manager.get('test')
        for item in updated_profile:
            self.assertIn(item, updated_profile)

    def tearDown(self):
        self.redis.delete('profile:test')
        self.redis.delete('profile:new_profile')


if __name__ == '__main__':
    unittest.main()
