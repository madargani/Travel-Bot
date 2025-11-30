from typing import List

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

load_dotenv()

tools = []

model = ChatOpenAI(model="gpt-5-nano", temperature=0, timeout=None, max_retries=2)

system_prompt = "You are a helpful assistant. Your job is to help plan a trip."

agent = create_agent(model, tools=tools, system_prompt=system_prompt)
