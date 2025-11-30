from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

# Instantiate model
model = ChatOpenAI(model="gpt-5-nano", temperature=0, timeout=None, max_retries=2)

# Bind tools
tools = []
tools_by_name = {tool.name: tool for tool in tools}
model_with_tools = model.bind_tools(tools)
