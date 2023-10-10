from air_pollution_mapper.api_caller.Client import Client
import unittest
import requests
from air_pollution_mapper.api_caller.utils import load_secrets


class TestClient(unittest.TestCase):
    def setUp(self):
        self.secrets = load_secrets()
        self.client = Client(key=self.secrets["GOOGLE_MAPS_API_KEY"])

    @unittest.skip
    def test_get(self):
        zoom = 6
        tile_coord = (4, 3)

        url = (
            "/v1/mapTypes/"
            + "US_AQI"
            + "/heatmapTiles/"
            + str(zoom)
            + "/"
            + str(tile_coord[0])
            + "/"
            + str(tile_coord[1])
        )

        request_url = self.client.compose_url(url)

        # Check url is formatted correctly
        self.assertEqual(
            request_url,
            "https://airquality.googleapis.com/v1/mapTypes/US_AQI/heatmapTiles/6/4/3?key={}".format(
                self.secrets["GOOGLE_MAPS_API_KEY"]
            ),
        )

        request_body = self.client.session.get(request_url)

        # check we get a dictionary returned
        self.assertIsInstance(
            request_body.headers, requests.structures.CaseInsensitiveDict
        )

        # check we get status 200
        self.assertEqual(request_body.status_code, 200)

        # check that we have got an image returned
        self.assertEqual(request_body.headers["Content-Type"], "image/png")

    @unittest.skip
    def test_post_currentConditions(self):
        params = {}
        location = {"latitude": 37.3, "longitude": -122.2}
        params["location"] = location
        url = "/v1/currentConditions:lookup"
        request_url = self.client.compose_url(url)
        request_header = self.client.compose_header()

        # Check url is formatted correctly
        self.assertEqual(
            request_url,
            "https://airquality.googleapis.com/v1/currentConditions:lookup?key={}".format(
                self.secrets["GOOGLE_MAPS_API_KEY"]
            ),
        )

        self.assertIsInstance(request_header, dict)

        response = self.client.session.post(
            request_url,
            headers=request_header,
            json=params,
        )

        # check we get status 200
        self.assertEqual(response.status_code, 200)

        self.assertIsInstance(response.json(), dict)

        self.assertEqual(len(response.json()["indexes"]), 1)

    @unittest.skip
    def test_post_historicalConditions(self):
        params = {}
        location = {"latitude": 37.3, "longitude": -122.2}
        params["location"] = location

        lag_time = 24
        params["hours"] = lag_time

        url = "/v1/history:lookup"
        request_url = self.client.compose_url(url)
        request_header = self.client.compose_header()

        print(request_url, request_header)

        # Check url is formatted correctly
        self.assertEqual(
            request_url,
            "https://airquality.googleapis.com/v1/history:lookup?key={}".format(
                self.secrets["GOOGLE_MAPS_API_KEY"]
            ),
        )

        self.assertIsInstance(request_header, dict)

        response = self.client.session.post(
            request_url,
            headers=request_header,
            json=params,
        )

        # check we get status 200
        self.assertEqual(response.status_code, 200)

        self.assertIsInstance(response.json(), dict)

        # lag time
        self.assertEqual(len(response.json()["hoursInfo"]), 24)

        self.assertEqual(len(response.json()["hoursInfo"][0]["indexes"]), 1)
