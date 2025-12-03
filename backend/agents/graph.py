import operator
from typing import Annotated, TypedDict, cast

from langchain.messages import AIMessage, AnyMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph


def create_agent(model: ChatOpenAI, tools, system_prompt: str):
    tools_by_name = {tool.name: tool for tool in tools}
    model_with_tools = model.bind_tools(tools)

    class MessagesState(TypedDict):
        messages: Annotated[list[AnyMessage], operator.add]
        llm_calls: int

    def llm_call(state: dict):
        return {
            "messages": [
                model_with_tools.invoke(
                    [SystemMessage(content=system_prompt)] + state["messages"]
                )
            ],
            "llm_calls": state.get("llm_calls", 0) + 1,
        }

    def tool_node(state: dict):
        result = []
        for tool_call in state["messages"][-1].tool_calls:
            tool = tools_by_name[tool_call["name"]]
            observation = tool.invoke(tool_call["args"])
            result.append(
                ToolMessage(content=observation, tool_call_id=tool_call["id"])
            )
        return {"messages": result}

    def should_continue(state: MessagesState):
        messages = state["messages"]
        last_message = cast(AIMessage, messages[-1])

        if last_message.tool_calls:
            return "tool_node"

        return END

    agent_builder = StateGraph(MessagesState)

    agent_builder.add_node("llm_call", llm_call)  # pyright: ignore
    agent_builder.add_node("tool_node", tool_node)  # pyright: ignore

    agent_builder.add_edge(START, "llm_call")
    agent_builder.add_conditional_edges("llm_call", should_continue, ["tool_node", END])
    agent_builder.add_edge("tool_node", "llm_call")

    return agent_builder.compile()
