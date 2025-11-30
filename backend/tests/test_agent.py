from pprint import pprint

from langchain.messages import HumanMessage

from agents.graph import agent
from agents.messages_state import MessagesState


def test_invoke():
    prompt: MessagesState = {
        "messages": [HumanMessage(content="Hello")],
        "llm_calls": 0,
    }
    response = agent.invoke(prompt)
    pprint(response["messages"][-1].content)
