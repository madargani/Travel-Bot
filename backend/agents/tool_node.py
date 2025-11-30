from langchain.messages import AIMessage, ToolMessage

from agents.messages_state import MessagesState
from agents.model import tools_by_name


def tool_call(state: MessagesState) -> MessagesState:
    assert isinstance(
        state["messages"][-1], AIMessage
    ), "Tool node did not receive AIMessage"

    result = []
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    return {"messages": result, "llm_calls": state["llm_calls"]}
