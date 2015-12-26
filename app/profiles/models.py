class ProfileManager():
    def __init__(self, db):
        self.db = db

    def create(self, profile_name, request_json):
        profile_list = request_json.get('lists')
        profile = self._parse_id(profile_name)
        self.db.lpush(profile, *profile_list)

    def get(self, profile_name):
        profile = self._parse_id(profile_name)
        return self.db.lrange(profile, 0, -1)

    def delete(self, profile_name):
        profile = self._parse_id(profile_name)
        self.db.delete(profile)

    def exists(self, profile_name):
        profile = self._parse_id(profile_name)
        if self.db.exists(profile):
            return True
        return False

    def _parse_id(self, profile_name):
        return "profile:%s" % profile_name
