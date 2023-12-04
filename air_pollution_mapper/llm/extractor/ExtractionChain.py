from typing import List, Optional
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain.utils.openai_functions import convert_pydantic_to_openai_function
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser


class Pollutant(BaseModel):
    """Information about an air pollutant"""

    name: str = Field(description="The name of the pollutant")


class Region(BaseModel):
    """Information about a country or region"""

    name: str = Field(description="The name of the region")


class DateRange(BaseModel):
    """
    The date range specified by the passage. If no date range is provided,
    assume that the end date is today and the start date is 3 days ago
    """

    start: str = Field(description="The start of the date range, in %Y-%m-%d format")
    end: str = Field(description="The end of the date range, in %Y-%m-%d format")


class Extraction(BaseModel):
    """Information to extract from a passage."""

    pollutants: Optional[List[Pollutant]] = Field(description="List of pollutants")
    regions: List[Region] = Field(description="List of regions")
    dates: Optional[List[DateRange]] = Field(description="List of date ranges")


class ExtractionChain(object):
    def __init__(self, llm):
        self.llm = llm

    @staticmethod
    def set_up_prompt():
        system_prompt = """
        You are an assistant who extracts relevant entities from questions and passages about air quality and pollution.
        Extract the relevant information. Extract partial information if needed.
        
        For the pollutants entity, you must choose from the following list:
        - Overall air quality index
        - Sulfur dioxide
        - Fine particulate matter (<2.5µm)
        - Inhalable particulate matter (<10µm)
        - Ozone
        - Nitrogen dioxide
        - Carbon monoxide
        """

        extraction_prompt = ChatPromptTemplate.from_messages(
            [("system", system_prompt), ("user", "{input}")]
        )

        return extraction_prompt

    def set_up_model(self):
        extraction_functions = [convert_pydantic_to_openai_function(Extraction)]

        extraction_model = self.llm.bind(
            functions=extraction_functions, function_call={"name": "Extraction"}
        )

        return extraction_model

    def set_up_chain(self):
        self.extraction_prompt = self.set_up_prompt()
        self.extraction_model = self.set_up_model()

        tagging_chain = (
            self.extraction_prompt | self.extraction_model | JsonOutputFunctionsParser()
        )

        return tagging_chain

    def generate(self):
        return self.set_up_chain()
