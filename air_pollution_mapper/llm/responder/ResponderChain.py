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


class ResponderChainWithContext(ResponderChain):
    @staticmethod
    def set_up_prompt():
        response_system_prompt = """
        You are an assistant who is an expert in air pollution, air quality and its associated health 
        effects. Use the following pieces of retrieved context to answer the question.
        If you don't know the answer, just say that you don't know.
        Use three sentences maximum and keep the answer concise.
        
        {context}
        """

        prompt = ChatPromptTemplate.from_messages(
            [("system", response_system_prompt), ("user", "{input}")]
        )

        return prompt
