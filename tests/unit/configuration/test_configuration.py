from swift_conductor.configuration import Configuration
import unittest


class TestConfiguration(unittest.TestCase):
    def test_initialization_default(self):
        configuration = Configuration()
        self.assertEqual(
            configuration.host,
            'http://localhost:8080/api'
        )

    def test_initialization_with_base_url(self):
        configuration = Configuration(
            base_url='http://localhost:8080'
        )
        self.assertEqual(
            configuration.host,
            'http://localhost:8080/api'
        )

    def test_initialization_with_server_api_url(self):
        configuration = Configuration(
            server_api_url='http://localhost:8080/api'
        )
        self.assertEqual(
            configuration.host,
            'http://localhost:8080/api'
        )

