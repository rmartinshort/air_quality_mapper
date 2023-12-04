import seaborn as sns
import matplotlib.pyplot as plt
from air_pollution_mapper.llm.AirQualityAgent import AirQualityAgent

class PollutionMapper(object):

    def __init__(self, openai_api_key, google_maps_api_key):

        self.parser = AirQualityAgent(
            openai_api_key=openai_api_key,
            google_maps_api_key=google_maps_api_key,
        )

        self.current_df = None
        self.current_display_map = None

    def pollutant_ts_seaborn(self, pollutant_code):

        # from global scope
        master_df = self.current_df

        fig = plt.figure(figsize=(10, 5))
        ax = fig.add_subplot(111)

        # if we want to show and AQI, pick the right one
        # use UAQI as a backup
        if pollutant_code == "index":
            df = master_df[master_df["type"] == "index"]
            indices = df["code"].unique().tolist()
            non_universal_index = [ind for ind in indices if ind != "uaqi"]
            if non_universal_index:
                choice_index = non_universal_index[0]
            else:
                choice_index = "uaqi"
            pollutant_code = choice_index

        df = master_df[master_df["code"] == pollutant_code]
        pollutant_name = df["name"].iloc[0]
        pollutant_unit = str(df["unit"].iloc[0]).lower().replace("_", " ")

        sns.lineplot(
            x="time",
            y="value",
            data=df,
            ax=ax,
            hue="region"
        )

        ax.set_title("{} : ({})".format(pollutant_name, pollutant_code))
        ax.set_xlabel("Time")
        ax.set_ylabel("Concentration [{}]".format(pollutant_unit))

        return fig

    def parse_for_UI(self, query, zoom_level):

        """
        Parse a query and return what is needed for the gradio UI
        :param query:
        :param zoom_level:
        :return:
        """

        response, df, health_suggestion, displaymap = self.parse(query, zoom_level)

        # if a pollutant has been requested
        if response["pollutant_codes"]:
            pollutant_code = response["pollutant_codes"][0]
        else:
            pollutant_code = "index"

        # get the response text if available
        if response["response"]:
            output_response = response["response"]
        else:
            output_response = response

        self.current_df = df
        self.current_display_map = displaymap
        self.current_response = response
        self.current_health_suggestion = health_suggestion

        plot_fig = self.pollutant_ts_seaborn(pollutant_code)

        return output_response, health_suggestion, displaymap, plot_fig

    def get_map(self):

        return self.current_display_map

    def get_response(self):

        return self.current_response

    def get_health_suggestion(self):

        return self.current_health_suggestion

    def get_conditions_df(self):

        return self.current_df

    def parse(self, query, zoom_level=7):

        response, df, health_suggestion, displaymap = self.parser.parse(query, zoom_level)

        return response, df, health_suggestion, displaymap