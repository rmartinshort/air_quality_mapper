import string
from air_pollution_mapper.llm.responder.ResponderChain import ResponderTimeseriesChain
import logging

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)


class TimeseriesResponder(object):
    DOWNSAMPLE_LEVELS = ["H", "2H", "4H", "8H", "16H", "D"]

    def __init__(self, llm):
        self.llm = llm
        self.responder_chain = ResponderTimeseriesChain(self.llm)
        self.responder = self.responder_chain.generate()

    @staticmethod
    def compress_table_to_string(df, use_hour=True):
        locations = [c for c in df.columns if c not in ["hour_since_start", "time"]]
        mapping_string = ""

        for i, element in enumerate(locations):
            mapping_string += "region {} is {}, ".format(
                string.ascii_uppercase[i], element
            )

        def text_from_row(row):
            if use_hour:
                res = str(row["hour_since_start"])
            else:
                res = str(row["time"]).split("+")[0].split(":")[0]

            for i, element in enumerate(locations):
                res += ":{} {}".format(string.ascii_uppercase[i], str(row[element]))

            return res

        encoded_ts = []
        for i, row in df.iterrows():
            encoded_ts.append(text_from_row(row))

        return ",".join(encoded_ts), mapping_string.strip()

    def check_token_thresh(self, filled_prompt, max_tokens=4000, verbose=True):
        ntokens = self.llm.get_num_tokens(filled_prompt)

        if verbose:
            logging.info("Counted {} tokens".format(ntokens))
        if ntokens > max_tokens:
            return False
        else:
            return True

    def downsample_timeseries(self, df):
        locations = [
            c for c in df.columns if c not in ["hour_since_start", "time", "date"]
        ]

        # loop through these resample levels so that we can decrease the length of the
        # timeseries that is sent to the LLM

        for level in self.DOWNSAMPLE_LEVELS:
            logging.info("Downsampling input timeseries to {}".format(level))
            tmp = df.copy()
            tmp = tmp.set_index("time")[locations].resample(level).mean().reset_index()
            df_string, region_map = self.compress_table_to_string(tmp, use_hour=False)

            # create a formatted prompt
            formatted_prompt = self.responder_chain.prompt.format(
                timeframe="hourly",
                metric="example metric",
                nregions="1",
                region_map="region A is Los Angeles CA",
                timeseries=df_string,
                input="example question",
            )

            # test number of tokens
            if self.check_token_thresh(formatted_prompt):
                break
            else:
                logging.info("Need to downsample again")

        return df_string, region_map, tmp, len(locations)

    def parse(self, query, df, pollutant):
        df_tmp = df[df["code"] == pollutant][["time", "value", "region"]]

        piv_tmp = df_tmp.pivot(
            index="time", columns="region", values="value"
        ).reset_index()

        ts_string, region_map, tmp, nlocations = self.downsample_timeseries(piv_tmp)

        res = self.responder.invoke(
            {
                "timeframe": "hourly",
                "metric": pollutant,
                "nregions": str(nlocations),
                "region_map": region_map,
                "timeseries": ts_string,
                "input": query,
            }
        )

        return res
