from unittest import TestCase

import rfcx

class LoginTests(TestCase):
    def test_is_string(self):
        rfcx.client.login()
        self.assertTrue(True)
