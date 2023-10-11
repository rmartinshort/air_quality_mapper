import math
import numpy as np


class TileHelper(object):
    def __init__(self, tile_size=256):
        self.tile_size = tile_size

    def location_to_tile_xy(self, location, zoom_level=4):
        """

        :param location:
        :param zoom_level:
        :return:
        """
        # Based on function here
        # https://developers.google.com/maps/documentation/javascript/examples/map-coordinates#maps_map_coordinates-javascript

        lat = location["latitude"]
        lon = location["longitude"]

        world_coordinate = self._project(lat, lon)
        scale = 1 << zoom_level

        pixel_coord = (
            math.floor(world_coordinate[0] * scale),
            math.floor(world_coordinate[1] * scale),
        )
        tile_coord = (
            math.floor(world_coordinate[0] * scale / self.tile_size),
            math.floor(world_coordinate[1] * scale / self.tile_size),
        )

        return world_coordinate, pixel_coord, tile_coord

    def tile_to_bounding_box(self, tx, ty, zoom_level):
        """

        :param tx:
        :param ty:
        :param zoom_level:
        :return:
        """
        # see https://developers.google.com/maps/documentation/javascript/coordinates
        # for details
        box_north = self._tiletolat(ty, zoom_level)
        # tile numbers advance towards the south
        box_south = self._tiletolat(ty + 1, zoom_level)
        box_west = self._tiletolon(tx, zoom_level)
        # time numbers advance towards the east
        box_east = self._tiletolon(tx + 1, zoom_level)

        # (latmin, latmax, lonmin, lonmax)
        return (box_south, box_north, box_west, box_east)

    @staticmethod
    def _tiletolon(x, zoom):
        """

        :param x:
        :param zoom:
        :return:
        """
        return x / math.pow(2.0, zoom) * 360.0 - 180.0

    @staticmethod
    def _tiletolat(y, zoom):
        """

        :param y:
        :param zoom:
        :return:
        """
        n = math.pi - (2.0 * math.pi * y) / math.pow(2.0, zoom)
        return math.atan(math.sinh(n)) * (180.0 / math.pi)

    def _project(self, lat, lon):
        """

        :param lat:
        :param lon:
        :return:
        """
        siny = math.sin(lat * math.pi / 180.0)
        siny = min(max(siny, -0.9999), 0.9999)

        return (
            self.tile_size * (0.5 + lon / 360),
            self.tile_size * (0.5 - math.log((1 + siny) / (1 - siny)) / (4 * math.pi)),
        )

    @staticmethod
    def find_nearest_corner(location, bounds):
        corner_lat_idx = np.argmin(
            [
                np.abs(bounds[0] - location["latitude"]),
                np.abs(bounds[1] - location["latitude"]),
            ]
        )

        corner_lon_idx = np.argmin(
            [
                np.abs(bounds[2] - location["longitude"]),
                np.abs(bounds[3] - location["longitude"]),
            ]
        )

        if (corner_lat_idx == 0) and (corner_lon_idx == 0):
            # closest is latmin, lonmin
            direction = "southwest"
        elif (corner_lat_idx == 0) and (corner_lon_idx == 1):
            # closest is latmax, lonmin
            direction = "southeast"
        elif (corner_lat_idx == 1) and (corner_lon_idx == 0):
            # closest is latmax, lonmin
            direction = "northwest"
        else:
            # closest is latmax, lonmax
            direction = "northeast"

        corner_coords = (bounds[corner_lat_idx], bounds[corner_lon_idx + 2])
        return corner_coords, direction

    @staticmethod
    def get_adjoining_tiles(tx, ty, direction):
        if direction == "southwest":
            return [(tx - 1, ty), (tx - 1, ty + 1), (tx, ty + 1)]
        elif direction == "southeast":
            return [(tx + 1, ty), (tx + 1, ty - 1), (tx, ty - 1)]
        elif direction == "northwest":
            return [(tx - 1, ty - 1), (tx - 1, ty), (tx, ty - 1)]
        else:
            return [(tx + 1, ty - 1), (tx + 1, ty), (tx, ty - 1)]
