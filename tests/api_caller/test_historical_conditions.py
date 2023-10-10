from air_pollution_mapper.api_caller.Client import Client
from air_pollution_mapper.api_caller.historical_conditions import historical_conditions
import unittest
from air_pollution_mapper.api_caller.utils import load_secrets


class TestCurrentConditions(unittest.TestCase):
    def setUp(self):
        self.secrets = load_secrets()
        self.client = Client(key=self.secrets["GOOGLE_MAPS_API_KEY"])

    # @unittest.skip
    def test_historical_conditions_lag(self):
        location = {"longitude": -122.3, "latitude": 37.8}
        lag_hours = 24

        historical_condition_resp = historical_conditions(
            self.client, location, lag_time=lag_hours
        )

        self.assertEqual(len(historical_condition_resp["hoursInfo"]), 24)
        self.assertEqual(
            len(historical_condition_resp["hoursInfo"][0]["pollutants"]), 6
        )
