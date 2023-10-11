from air_pollution_mapper.api_caller.TileHelper import TileHelper
import numpy as np


def air_quality_tile(
    client, location, pollutant="UAQI_INDIGO_PERSIAN", zoom=4, get_adjoining_tiles=True
):
    """
    See documentation for this API here https://developers.google.com/maps/documentation/air-quality/reference/rest/v1/mapTypes.heatmapTiles/lookupHeatmapTile
    :param client:
    :param location:
    :param pollutant:
    :param zoom:
    :return:
    """
    # see https://developers.google.com/maps/documentation/air-quality/reference/rest/v1/mapTypes.heatmapTiles/lookupHeatmapTile

    assert pollutant in [
        "UAQI_INDIGO_PERSIAN",
        "UAQI_RED_GREEN",
        "PM25_INDIGO_PERSIAN",
        "GBR_DEFRA",
        "DEU_UBA",
        "CAN_EC",
        "FRA_ATMO",
        "US_AQI",
    ]

    # contains useful methods for dealing the tile coordinates
    helper = TileHelper()

    # get the tile that the location is in
    world_coordinate, pixel_coord, tile_coord = helper.location_to_tile_xy(
        location, zoom_level=zoom
    )

    # get the bounding box of the tile
    bounding_box = helper.tile_to_bounding_box(
        tx=tile_coord[0], ty=tile_coord[1], zoom_level=zoom
    )

    if get_adjoining_tiles:
        # gather the three closest tiles in addition to the one where the coordinates lie
        # then we can be sure of good coverage on the map
        nearest_corner, nearest_corner_direction = helper.find_nearest_corner(
            location, bounding_box
        )
        adjoining_tiles = helper.get_adjoining_tiles(
            tile_coord[0], tile_coord[1], nearest_corner_direction
        )
    else:
        adjoining_tiles = []

    tiles = []
    # get all the adjoining tiles, plus the one in question
    for tile in adjoining_tiles + [tile_coord]:
        bounding_box = helper.tile_to_bounding_box(
            tx=tile[0], ty=tile[1], zoom_level=zoom
        )
        image_response = client._request_get(
            "/v1/mapTypes/"
            + pollutant
            + "/heatmapTiles/"
            + str(zoom)
            + "/"
            + str(tile[0])
            + "/"
            + str(tile[1])
        )

        # convert the PIL image to numpy
        try:
            image_response = np.array(image_response)
        except:
            image_response = None

        tiles.append({"bounds": bounding_box, "image": image_response})

    return tiles
