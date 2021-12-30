import unittest

import pytest

from pridepy.authentication import Authentication


class TestAuthentication(unittest.TestCase):
    """
    A test class to test Authentication related methods.
    """

    @pytest.mark.skip(reason="Needs credentials")
    def test_get_token(self):
        """
        Test get API AAP token functionality
        :return:
        """
        username = "anil@ibioinformatics.org"
        password = "tvYkX34H"
        auth = Authentication()
        api_token = auth.get_token(username, password)
        print(api_token)
        self.assertTrue(len(api_token) > 20, "Token not found!")

    @pytest.mark.skip(reason="Needs credentials")
    def test_validate_token(self):
        """
        Test get API AAP token is valid or expired
        :return:
        """
        username = "anil@ibioinformatics.org"
        password = "tvYkX34H"
        auth = Authentication()
        api_token = auth.get_token(username, password)
        print(api_token)
        self.assertTrue(auth.validate_token(api_token), "Token is invalid or expired!")


if __name__ == '__main__':
    unittest.main()
