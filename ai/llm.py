import os
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from ai.config import SYSTEM_PROMPT
from ai.tools import llm_tools
from langchain.agents import create_tool_calling_agent, AgentExecutor

load_dotenv()

class LLM():
    def __init__(self):
        self.tools = []
        self.chat = ChatGroq(temperature=0, model_name="mixtral-8x7b-32768").bind_tools(self.tools)
        self.system_prompt = SYSTEM_PROMPT
        self.agent_prompt = prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt), 
            ("human", "{input}"), 
            ("placeholder", "{agent_scratchpad}"),
        ])
        self.agent = create_tool_calling_agent(self.chat, self.tools, self.agent_prompt)
        self.executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)
        
    def get_ctx(self, ctx):
        self.ctx = ctx
    
    def ask_ai(self, query):
        response = self.executor.invoke({"input": query})
        return response['output']