import googlemaps
from datetime import datetime


class ExtractionEnricher(object):
    def __init__(self, google_maps_api_key):
        self.gmaps_client = googlemaps.Client(key=google_maps_api_key)

    def convert_to_coords(self, input_address):
        geocoded = self.gmaps_client.geocode(input_address)
        if len(geocoded) > 0:
            return self.extract_coordinates_from_geocoded(geocoded)
        else:
            return {"latitude": 0, "longitude": 0}

    @staticmethod
    def extract_coordinates_from_geocoded(geocoded):
        place = geocoded[0]
        if "geometry" in place:
            location = place["geometry"]
            if "bounds" in location:
                ne_lat, ne_lon = location["bounds"]["northeast"].values()
                sw_lat, sw_lon = location["bounds"]["southwest"].values()
                lat = (float(ne_lat) + float(sw_lat)) / 2
                lon = (float(ne_lon) + float(sw_lon)) / 2
            else:
                ne_lat, ne_lon = location["viewport"]["northeast"].values()
                sw_lat, sw_lon = location["viewport"]["southwest"].values()
                lat = (float(ne_lat) + float(sw_lat)) / 2
                lon = (float(ne_lon) + float(sw_lon)) / 2

            lon = round(lon, 4)
            lat = round(lat, 4)

            return {"latitude": lat, "longitude": lon}

        else:
            return {"latitude": 0, "longitude": 0}

    def parse(self, result):
        locations = result["regions"]
        pollutants = result["pollutants"]

        # extract region coordinates
        region_coords = {}
        for region in locations:
            region_name = region["name"]
            region_coords[region_name] = self.convert_to_coords(region_name)

        # get the number of hours of lag to send to API
        try:
            # dates may not be present. If so this will fail
            dates = result["dates"][0]
            number_of_hours_lag = min(
                720,
                max(
                    24,
                    (
                        datetime.strptime(dates["end"], "%Y-%m-%d")
                        - datetime.strptime(dates["start"], "%Y-%m-%d")
                    ).total_seconds()
                    // 3600,
                ),
            )
        except:
            number_of_hours_lag = 24

        # get the pollutant codes
        pollutant_codes = []
        if pollutants:
            for pollutant in pollutants:
                pollutant_codes.append(pollutant)

        return pollutant_codes, number_of_hours_lag, region_coords
