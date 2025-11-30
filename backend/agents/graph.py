from typing import Literal

from langchain.messages import AIMessage
from langgraph.graph import END, START, StateGraph

from agents.messages_state import MessagesState
from agents.model_node import llm_call
from agents.tool_node import tool_call


def should_continue(state: MessagesState) -> Literal["tool_node", "__end__"]:
    """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""

    messages = state["messages"]
    last_message = messages[-1]

    # If the LLM makes a tool call, then perform an action
    assert isinstance(last_message, AIMessage)
    if last_message.tool_calls:
        return "tool_node"

    # Otherwise, we stop (reply to the user)
    return "__end__"


# Build workflow
agent_builder = StateGraph(MessagesState)

# Add nodes
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("tool_node", tool_call)

# Add edges to connect nodes
agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges("llm_call", should_continue, ["tool_node", END])
agent_builder.add_edge("tool_node", "llm_call")

# Compile the agent
agent = agent_builder.compile()
