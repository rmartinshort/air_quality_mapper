from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser


class ResponderChain(object):
    def __init__(self, llm):
        self.llm = llm

    @staticmethod
    def set_up_prompt():
        response_system_prompt = """
        You are an assistant who is an expert in air pollution, air quality and its associated health 
        effects. Answer the following question, using three sentences maximum to keep the answer concise.
        """

        prompt = ChatPromptTemplate.from_messages(
            [("system", response_system_prompt), ("user", "{input}")]
        )

        return prompt

    def set_up_chain(self):
        self.prompt = self.set_up_prompt()

        response_chain = self.prompt | self.llm | StrOutputParser()

        return response_chain

    def generate(self):
        return self.set_up_chain()


class ResponderChainWithAPI(object):
    def __init__(self, llm):
        self.llm = llm

    @staticmethod
    def set_up_prompt():
        response_system_prompt = """
        You are an assistant who is an expert in air pollution, air quality and its associated health 
        effects. Answer the following question, using three sentences maximum to keep the answer concise.

        Note that you have access to the Google Maps Air Quality API, which allows you to answer questions about
        specific pollutants at specific locations. If the query can be answered using this API, describe how you will
        do so. Another agent will then follow the plan you create.
        """

        prompt = ChatPromptTemplate.from_messages(
            [("system", response_system_prompt), ("user", "{input}")]
        )

        return prompt

    def set_up_chain(self):
        self.prompt = self.set_up_prompt()

        response_chain = self.prompt | self.llm | StrOutputParser()

        return response_chain

    def generate(self):
        return self.set_up_chain()


class ResponderTimeseriesChain(ResponderChain):
    @staticmethod
    def set_up_prompt():
        response_system_prompt = """
        You are a helpful assistant who helps interpret timeseries. 

        You will be given a timeseries encoded as a string. 
        Think carefully about the question and the timseries then answer concisely using a maximum of 4 sentences. 
        Do not make up answers, use only the information in the timeseries.

        {region_map}

        Use the actual region names in your answer rather than the letters in the timeseries string.

        To help you decode the timeseries, use the following information:

        You are given {timeframe} data for {metric} in {nregions} regions. It is encoded as a string 
        where each time point is separated by a comma and each region is represented by a letter

        For example, the string

        "2023-12-12 01:A45:B24,2023-12-12 02:A54:B30"

        should be interpreted as 
        at 1am on 2023-12-12, regions A's value is 45 and region B's value is 24
        at 2am on 2023-12-12, regions A's value is 54 and region B's value is 30

        Timeseries: {timeseries}
        """

        prompt = ChatPromptTemplate.from_messages(
            [("system", response_system_prompt), ("user", "{input}")]
        )

        return prompt
