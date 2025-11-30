import operator

from langchain.messages import AnyMessage
from typing_extensions import Annotated, TypedDict


# Define state
class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int
