import math


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
