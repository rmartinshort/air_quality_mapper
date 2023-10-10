from air_pollution_mapper.api_caller.TileHelper import TileHelper
import unittest
from air_pollution_mapper.api_caller.utils import load_secrets


class TestTileHelper(unittest.TestCase):
    def setUp(self):
        self.secrets = load_secrets()
        self.tile_setup = TileHelper()

    def test_location_to_tile_xy(self):
        location = {"longitude": -122.3, "latitude": 37.8}
        world_coords, xy_coords, tile_xy = self.tile_setup.location_to_tile_xy(
            location, zoom_level=1
        )

        self.assertEqual(world_coords[0], 41.031111111111116)
        self.assertEqual(world_coords[1], 98.92677453930035)

        self.assertEqual(xy_coords[0], 82)
        self.assertEqual(xy_coords[1], 197)

        self.assertEqual(tile_xy[0], 0)
        self.assertEqual(tile_xy[1], 0)

    def test_tile_to_bounding_box(self):
        min_lat, max_lat, min_lon, max_lon = self.tile_setup.tile_to_bounding_box(
            1, 1, 1
        )

        self.assertEqual(min_lat, -85.0511287798066)
        self.assertEqual(max_lat, 0)
        self.assertEqual(min_lon, 0)
        self.assertEqual(max_lon, 180.0)
