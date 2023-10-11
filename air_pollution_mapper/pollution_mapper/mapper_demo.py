import leafmap.foliumap as leafmap
import folium
from air_pollution_mapper.api_caller.Client import Client
from air_pollution_mapper.api_caller.air_quality_heatmap_tile import air_quality_tile
from air_pollution_mapper.api_caller.utils import load_secrets
from air_pollution_mapper.constants import MAPS_DUMP_DIR
import os


def main():
    secrets = load_secrets()
    client = Client(key=secrets["GOOGLE_MAPS_API_KEY"])

    # get the lat, lon and zoom
    zoom = 8
    lat = 37.8
    lon = -121.8

    location = {"latitude": lat, "longitude": lon}

    # get the tiles
    tiles = air_quality_tile(
        client,
        location,
        pollutant="UAQI_INDIGO_PERSIAN",
        zoom=zoom,
        get_adjoining_tiles=True,
    )

    map = leafmap.Map(location=[lat, lon], tiles="OpenStreetMap", zoom_start=zoom)

    # add all the tiles that we just made
    for tile in tiles:
        latmin, latmax, lonmin, lonmax = tile["bounds"]
        AQ_image = tile["image"]
        folium.raster_layers.ImageOverlay(
            image=AQ_image, bounds=[[latmin, lonmin], [latmax, lonmax]], opacity=0.8
        ).add_to(map)

    # save to test location
    map.to_html(os.path.join(MAPS_DUMP_DIR, "test_route_map.html"))
