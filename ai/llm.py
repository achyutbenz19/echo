import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from ai.config import SYSTEM_PROMPT

load_dotenv()

class LLM():
    def __init__(self):
        self.chat = ChatGroq(temperature=0, model_name="mixtral-8x7b-32768")
        self.system_prompt = SYSTEM_PROMPT
        self.human = "{text}"
        self.prompt = ChatPromptTemplate.from_messages([("system", self.system_prompt), ("human", self.human)])
        
    def get_ctx(ctx):
        self.ctx = ctx
    
    def ask_ai(self, query):
        chain = self.prompt | self.chat
        return chain.invoke({"text": query}).content
    