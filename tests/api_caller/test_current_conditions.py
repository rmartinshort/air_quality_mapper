from air_pollution_mapper.api_caller.Client import Client
from air_pollution_mapper.api_caller.current_conditions import current_conditions
import unittest
from air_pollution_mapper.api_caller.utils import load_secrets


class TestCurrentConditions(unittest.TestCase):
    def setUp(self):
        self.secrets = load_secrets()
        self.client = Client(key=self.secrets["GOOGLE_MAPS_API_KEY"])

    @unittest.skip
    def test_current_conditions(self):
        location = {"longitude": -122.3, "latitude": 37.8}

        current_condition_resp = current_conditions(self.client, location)

        # make sure we get all the indexes
        self.assertEqual(len(current_condition_resp["indexes"]), 2)

        # make sure we get all the pollutants
        self.assertEqual(len(current_condition_resp["pollutants"]), 6)
