from langchain.messages import SystemMessage

from agents.messages_state import MessagesState
from agents.model import model_with_tools


def llm_call(state: MessagesState) -> MessagesState:
    """LLM decides whether to call a tool or not"""
    return {
        "messages": [
            model_with_tools.invoke(
                [
                    SystemMessage(
                        content="You are an assistant tasked with helping book flights."
                    )
                ]
                + state["messages"]
            )
        ],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }
