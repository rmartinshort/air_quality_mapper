from itertools import chain
import pandas as pd


def historical_conditions_to_df(response_dict):
    """
    Take output from historical conditions and convert to dataframe
    :param response_dict:
    :return:
    """

    chained_pages = list(
        chain(*[response_dict[p]["hoursInfo"] for p in [*response_dict]])
    )

    all_indexes = []
    all_pollutants = []
    for i in range(len(chained_pages)):
        # need this check in case one of the timestamps is missing data, which can sometimes happen
        if "indexes" in chained_pages[i]:
            this_element = chained_pages[i]
            # fetch the time
            time = this_element["dateTime"]
            # fetch all the index values and add metadata
            all_indexes += [
                (time, x["code"], x["displayName"], "index", x["aqi"], None)
                for j, x in enumerate(this_element["indexes"])
            ]
            # fetch all the pollutant values and add metadata
            all_pollutants += [
                (
                    time,
                    x["code"],
                    x["fullName"],
                    "pollutant",
                    x["concentration"]["value"],
                    x["concentration"]["units"],
                )
                for j, x in enumerate(this_element["pollutants"])
            ]

    all_results = all_indexes + all_pollutants
    # generate "long format" dataframe
    res = pd.DataFrame(
        all_results, columns=["time", "code", "name", "type", "value", "unit"]
    )
    res["time"] = pd.to_datetime(res["time"])
    return res
