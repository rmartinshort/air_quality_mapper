from air_pollution_mapper.llm.tagger.TaggingChain import TaggingChain
from air_pollution_mapper.llm.extractor.ExtractionChain import ExtractionChain
from air_pollution_mapper.llm.extractor.ExtractionEnricher import ExtractionEnricher
from air_pollution_mapper.llm.responder.ResponderChain import (
    ResponderChain,
    ResponderChainWithContext,
    ResponderChainWithAPI,
)
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chat_models import ChatOpenAI
from datetime import datetime
import logging

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)


class QueryHandler(object):
    def __init__(
        self, openai_api_key, google_maps_api_key, model="gpt-3.5-turbo", temperature=0
    ):
        self.extractor_model = ChatOpenAI(
            temperature=temperature, model_name=model, openai_api_key=openai_api_key
        )
        self.responder_model = ChatOpenAI(
            model_name=model,
            temperature=temperature,
            openai_api_key=openai_api_key,
            streaming=True,
            callbacks=[StreamingStdOutCallbackHandler()],
        )
        self.tagger = TaggingChain(self.extractor_model).generate()
        self.extractor = ExtractionChain(self.extractor_model).generate()
        self.enricher = ExtractionEnricher(google_maps_api_key=google_maps_api_key)
        self.responder = ResponderChain(self.responder_model).generate()
        self.api_responder = ResponderChainWithAPI(self.responder_model).generate()

    def question_type_handler(self, question_type):
        extract = False
        get_healthcare = False
        broad = False

        if not question_type:
            return False, False, False
        else:
            question_type_list = [x["name"] for x in question_type]

            if "invalid" in question_type_list:
                return False, False, False

            if "region" in question_type_list:
                extract = True
            elif "broad" in question_type_list:
                extract = False
                broad = True

            if "healthcare" in question_type_list:
                get_healthcare = True

        return extract, get_healthcare, broad

    def handle_invalid(self):
        result = {
            "response": "This query is invalid",
            "pollutant_codes": [],
            "nhours_lag": 0,
            "regions": [],
            "health_suggestion": None,
        }

        return result

    def tag(self, query):
        tagged_result = self.tagger.invoke({"input": query})
        return tagged_result

    def extract(self, query):
        todays_time = str(datetime.now())
        enriched_query = query + ". Note that the time now is {}".format(todays_time)
        extracted_result = self.extractor.invoke({"input": enriched_query})
        return extracted_result

    def respond(self, query, api_call=False):
        if api_call:
            response = self.api_responder.invoke({"input": query})
        else:
            response = self.responder.invoke({"input": query})
        return response

    def parse(self, query):
        tagged_result = self.tag(query)

        logging.info("Query tags: {}".format(tagged_result))

        extract, get_healthcare, broad = self.question_type_handler(
            tagged_result["question_type"]
        )

        logging.info(
            "Extract : {}, Get_healthcare :{}, Broad: {}".format(
                extract, get_healthcare, broad
            )
        )

        if not extract and not get_healthcare and not broad:
            # query is invalid
            return self.handle_invalid()

        if extract:
            extracted_result = self.extract(query)
            logging.info("Query extractions: {}".format(extracted_result))
            pollutant_codes, number_of_hours_lag, region_coords = self.enricher.parse(
                extracted_result
            )
            logging.info(
                "Query enriched extractions: {}, {}, {}".format(
                    pollutant_codes, number_of_hours_lag, region_coords
                )
            )
            # get a text response to the query too
            response_wo_context = self.respond(query, api_call=True)
        else:
            response_wo_context = self.respond(query, api_call=False)
            # extract regions and pollutants from the response, in case they are present
            extracted_result = self.extract(response_wo_context)
            pollutant_codes, number_of_hours_lag, region_coords = self.enricher.parse(
                extracted_result
            )

        result = {
            "response": response_wo_context,
            "pollutant_codes": pollutant_codes,
            "nhours_lag": number_of_hours_lag,
            "regions": region_coords,
            "health_suggestion": get_healthcare,
        }

        return result
