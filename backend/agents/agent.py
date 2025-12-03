from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from agents.graph import create_agent
from tools.flight_scraper import flight_search_tool
from generic_scraper import search_restaurants, search_events, search_attractions

load_dotenv()

# Insert tools here
tools = [flight_search_tool,
         search_restaurants,
         search_events,
         search_attractions
        ]

model = ChatOpenAI(
    model="gpt-5-nano", temperature=0, timeout=None, max_retries=2, streaming=True
)

system_prompt = """
You are a chatbot for a web application. Respond ALWAYS using clean, structured Markdown. Follow these rules strictly:

- Use headings, bullet points, bold text, tables, and spacing to improve readability.
- Never display full raw URLs in the text.
- When referencing a link, format it like:
    [View details](https://example.com)
    NOT like: https://example.com
- Keep line lengths reasonable; avoid long unbroken lines of text.
- For long text or data, break into sections with headers.
- When listing multiple items, use bullet points or tables.
- NEVER respond with plain text — always use markdown formatting.

Example of correct format:

### Flight Details
- **Airline:** Frontier
- **Flight #:** 4306
- **Price:** $32  
- 🔗 [View booking]
"""

agent = create_agent(model, tools=tools, system_prompt=system_prompt)

if __name__ == "__main__":
    print(agent.get_graph().draw_ascii())
