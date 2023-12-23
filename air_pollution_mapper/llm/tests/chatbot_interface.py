from operator import itemgetter
import os
import time
from air_pollution_mapper.llm.utils import load_secrets, assert_secrets
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.schema.runnable import RunnableLambda, RunnablePassthrough

# Initialize chat model
secrets = load_secrets()
llm = ChatOpenAI(openai_api_key=secrets["OPENAI_API_KEY"])

# Define a prompt template
template = """You are a helpful AI assistant. You give specialized advice on travel.
"""

chat_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", template),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)

# Create conversation history store
memory = ConversationBufferMemory(memory_key="history", return_messages=True)

chain = (
    RunnablePassthrough.assign(
        history=RunnableLambda(memory.load_memory_variables) | itemgetter("history")
    )
    | chat_prompt
    | llm
)


# UI
import gradio as gr
import random

import gradio as gr
import random
import time

with gr.Blocks() as demo:
    chatbot = gr.Chatbot()
    msg = gr.Textbox()
    clear = gr.ClearButton([msg, chatbot])

    def respond(message, chat_history):
        bot_message = random.choice(["How are you?", "I love you", "I'm very hungry"])
        chat_history.append((message, bot_message))
        time.sleep(2)
        return "", chat_history

    msg.submit(respond, [msg, chatbot], [msg, chatbot])

demo.launch()
