from pprint import pprint

from langchain.messages import HumanMessage

from agents.agent import agent


def test_invoke():
    prompt = {"messages": [HumanMessage(content="Hello")]}
    response = agent.invoke(prompt)  # type: ignore
    pprint(response["messages"][-1].content)
