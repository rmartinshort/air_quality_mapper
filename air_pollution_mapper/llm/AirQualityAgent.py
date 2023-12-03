from air_pollution_mapper.llm.QueryHandler import QueryHandler
from air_pollution_mapper.api_caller.Client import Client
import pandas as pd
import seaborn as sns
from air_pollution_mapper.api_caller.historical_conditions import historical_conditions
from air_pollution_mapper.api_caller.air_quality_heatmap_tile import air_quality_tile
from air_pollution_mapper.pollution_timeseries.utils import historical_conditions_to_df
import matplotlib.pyplot as plt
import folium
import leafmap.foliumap as leafmap
import logging

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)


class AirQualityAgent(object):
    def __init__(
        self, openai_api_key, google_maps_api_key, model="gpt-3.5-turbo", temperature=0
    ):
        self.query_parser = QueryHandler(
            openai_api_key=openai_api_key,
            google_maps_api_key=google_maps_api_key,
            model=model,
            temperature=temperature,
        )
        self.air_quality_client = Client(key=google_maps_api_key)

    def get_conditions_from_locations(
        self, region_coords, lag_hours, health_suggestion=False
    ):
        all_series = []
        for location_name, location_coords in region_coords.items():
            history_conditions_data = historical_conditions(
                self.air_quality_client,
                location_coords,
                lag_time=lag_hours,
                include_health_suggestion=health_suggestion,
            )

            if health_suggestion:
                pages = sorted(list(history_conditions_data.keys()))
                health_recommentations_text = history_conditions_data[pages[-1]][
                    "hoursInfo"
                ][-1]["healthRecommendations"]
            else:
                health_recommentations_text = ""

            try:
                historical_df = historical_conditions_to_df(history_conditions_data)
            except:
                historical_df = pd.DataFrame(
                    {
                        "time": [],
                        "code": [],
                        "name": [],
                        "type": [],
                        "value": [],
                        "unit": [],
                    }
                )

            pollutants = historical_df
            pollutants["region"] = location_name
            all_series.append(pollutants)

        pollutants = pd.concat(all_series)

        return pollutants, health_recommentations_text

    def get_tiles_from_locations(self, region_coords, zoom, pollutant="US_AQI"):
        all_tiles = {}
        for location_name, location_coords in region_coords.items():
            tiles = air_quality_tile(
                self.air_quality_client,
                location_coords,
                pollutant=pollutant,
                zoom=zoom,
                get_adjoining_tiles=True,
            )

            all_tiles[location_name] = tiles

        return all_tiles

    @staticmethod
    def pollutant_tiles_to_map(heatmap, region_coords, zoom):
        # from global scope
        location_tiles = heatmap

        region_keys = list(region_coords.keys())
        central_coords = region_coords[region_keys[0]]

        map = leafmap.Map(
            location=[central_coords["latitude"], central_coords["longitude"]],
            tiles="OpenStreetMap",
            zoom_start=zoom,
        )

        # add each location
        for location, tiles in location_tiles.items():
            # add the heatmap tiles
            for i, tile in enumerate(tiles):
                latmin, latmax, lonmin, lonmax = tile["bounds"]
                # name the tile so that this shows up on the map layers
                tile_name = "{}_heatmap_tile_{}".format(location, str(i + 1))
                AQ_image = tile["image"]
                folium.raster_layers.ImageOverlay(
                    image=AQ_image,
                    name=tile_name,
                    bounds=[[latmin, lonmin], [latmax, lonmax]],
                    opacity=0.7,
                ).add_to(map)

        # add marker for each location
        for location_name, location_coords in region_coords.items():
            folium.Marker(
                location=[location_coords["latitude"], location_coords["longitude"]],
                popup=location_name,
                icon=folium.Icon(color="red", icon="info-sign"),
            ).add_to(map)

        return map.to_gradio()

    @staticmethod
    def pollutant_ts_seaborn(conditions_df, pollutant_code):
        fig = plt.figure(figsize=(10, 5))
        ax = fig.add_subplot(111)

        # if we want to show and AQI, pick the right one
        # use UAQI as a backup
        if pollutant_code == "index":
            df = conditions_df[conditions_df["type"] == "index"]
            indices = df["code"].unique().tolist()
            non_universal_index = [ind for ind in indices if ind != "uaqi"]
            if non_universal_index:
                choice_index = non_universal_index[0]
            else:
                choice_index = "uaqi"
            pollutant_code = choice_index

        df = conditions_df[conditions_df["code"] == pollutant_code]
        pollutant_name = df["name"].iloc[0]
        pollutant_unit = str(df["unit"].iloc[0]).lower().replace("_", " ")

        sns.lineplot(x="time", y="value", data=df, ax=ax, hue="region")

        ax.set_title("{} : ({})".format(pollutant_name, pollutant_code))
        ax.set_xlabel("Time")
        ax.set_ylabel("Concentration [{}]".format(pollutant_unit))

        return fig

    def generate_heatmap(self, regions, zoom):
        pollutant_heatmap_tiles = self.get_tiles_from_locations(
            region_coords=regions, zoom=zoom
        )
        pollutant_heatmap = self.pollutant_tiles_to_map(
            pollutant_heatmap_tiles, regions, zoom
        )
        return pollutant_heatmap

    def generate_pollutant_timeseries(self, regions, nhours, health_suggestion):
        (
            historical_pollutant_conditions,
            health_suggestion_response,
        ) = self.get_conditions_from_locations(
            region_coords=regions,
            lag_hours=nhours,
            health_suggestion=health_suggestion,
        )

        return historical_pollutant_conditions, health_suggestion_response

    def parse(self, query):
        logging.info("LLM parse {}".format(query))
        llm_result = self.query_parser.parse(query)
        logging.info("LLM result: {}".format(llm_result))

        regions = llm_result["regions"]
        nhours = llm_result["nhours_lag"]
        pollutant_codes = llm_result["pollutant_codes"]
        health_suggestion = llm_result["health_suggestion"]
        zoom = 7

        if regions:
            logging.info("API call to google air quality for historical conditions")
            # if we have something to plot, then gather the data from the air quality API
            (
                conditions_df,
                health_suggestion_response,
            ) = self.generate_pollutant_timeseries(regions, nhours, health_suggestion)
            logging.info("API call to google air quality for heatmaps")
            heatmap = self.generate_heatmap(regions, zoom)

            return llm_result, conditions_df, health_suggestion_response, heatmap

        else:
            return llm_result, None, None, None
