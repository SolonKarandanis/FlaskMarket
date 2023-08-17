from market import app
from market.data_access.models.models import User

import unittest


class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='susan', email_address='asd@hot.com', password='cat')
        self.assertFalse(u.check_password_correction('dog'))
        self.assertTrue(u.check_password_correction('cat'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
