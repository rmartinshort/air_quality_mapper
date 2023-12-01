from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain.utils.openai_functions import convert_pydantic_to_openai_function
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser


class QueryTagging(BaseModel):
    """Tag this query"""

    question_type: str = Field(
        description="The classification of the query. Must be one of 'invalid', 'helpcenter', 'single' or 'group'"
    )
    language: str = Field(
        description="language of the query (should be ISO 639-1 code)"
    )


class TaggingChain(object):
    def __init__(self, llm):
        self.llm = llm

    @staticmethod
    def set_up_prompt(self):
        tagging_system_prompt = """
          You are an assistant who is an expert in air pollution, air quality and its associated health 
          effects. You have access to an API that can provide air quality information given a location and timeframe.
          Think carefully, then tag the following query according to the instructions.

          To help you classify the query and select the correct question_type tag, use the following information:

          There are four possible question types and you must choose at least one. 

          - invalid: The question is not about about air quality
          - healthcare: The question is about an aspect of air quality related to human health
          - region: The question contains the names of one or more cities, countries of regions
          - broad: The question is about air quality but does not mention any specific region

          Here are some examples:

          "My grandma has asthma, can she safely go outside in Seattle right now?" Should be tagged as "healthcare" and "region"
          "What are the carbon monoxide levels in downtown Los Angeles over the last 24 hours?" Should be tagged as "regipn"
          "What are the cities with the cleanest air?" Should be tagged as "broad"
          "Whats the price of milk in Tokyo?" Should be tagged as "invalid"

        """

        tagging_prompt = ChatPromptTemplate.from_messages(
            [("system", tagging_system_prompt), ("user", "{input}")]
        )

        return tagging_prompt

    @staticmethod
    def set_up_model(self):
        tagging_functions = [convert_pydantic_to_openai_function(QueryTagging)]

        tagging_model = self.llm.bind(
            functions=tagging_functions, function_call={"name": "QueryTagging"}
        )

        return tagging_model

    def set_up_chain(self):
        self.tagging_prompt = self.set_up_prompt()
        self.tagging_model = self.set_up_model()

        tagging_chain = (
            self.tagging_prompt | self.tagging_model | JsonOutputFunctionsParser()
        )

        return tagging_chain

    def generate(self):
        return self.set_up_chain()
