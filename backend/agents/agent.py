from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from agents.graph import create_agent
from tools.flight_scraper import flight_search_tool

load_dotenv()

# Insert tools here
tools = [flight_search_tool]

model = ChatOpenAI(
    model="gpt-5-nano", temperature=0, timeout=None, max_retries=2, streaming=True
)

system_prompt = """
You are a helpful assistant. Be concise and considerate.
When calling tools, you may return structured JSON to the system.
But when speaking to the user, you must respond in plain natural language.
Never expose raw JSON from tools to the user. Summarize it in human-readable form.
"""

agent = create_agent(model, tools=tools, system_prompt=system_prompt)

if __name__ == "__main__":
    print(agent.get_graph().draw_ascii())
