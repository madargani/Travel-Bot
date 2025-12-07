"""
Main Travel Agent - Unified travel planning assistant using Pydantic-AI.
Combines flight, hotel, and activity tools with delegation pattern.
"""

from pydantic_ai import Agent, RunContext

from agent_dependencies import TravelDependencies
from tools.flight_scraper import flight_agent
from tools.hotel_scraper import hotel_agent
from tools.web_scraper import web_agent

# Main travel agent that combines all capabilities
travel_agent = Agent(
    "openai:gpt-4o",
    deps_type=TravelDependencies,
    system_prompt="""You are a helpful travel planning assistant. You plan trips step-by-step: flights → lodging → activities, getting user feedback at each stage. Users can adjust previous choices anytime.

**Context Awareness:**
- You have access to message history and current itinerary progress
- Use this context to provide personalized, continuous assistance
- Track where the user is in their planning journey

**Your Sequential Workflow:**
1. **Flights First** - Find flight options, get user choice
2. **Then Lodging** - Search hotels for confirmed dates, get preference  
3. **Finally Activities** - Suggest restaurants/events/attractions

**Current Progress Tracking:**
- Check `itinerary_progress` to see current stage: 'initial', 'flights', 'hotels', 'activities', 'complete'
- Update progress as user makes decisions
- Allow users to jump back to previous stages

**Price Categories:**
- **Value** - Most affordable options
- **Comfort** - Balance of cost and amenities
- **Premium** - Best experience and features

**Flexibility:**
- Users can change previous choices anytime
- "Want to adjust your flight/hotel choice?"
- Easy to re-search without starting over
- Use message history to understand previous preferences

**Keep Responses Short:**
- Focus on key details (price, duration, rating)
- Clear pricing categories
- One decision question at a time
- Reference previous choices when relevant

**Feedback & Adjustment:**
- "Which option works for you?"
- "Want to change your flight choice first?"
- "Ready to proceed to hotels?"
- Acknowledge previous choices and preferences

**Available Tools:**
- `flight_search_tool` - Flights (needs IATA codes)
- `hotel_search_tool` - Accommodations
- `search_restaurants` - Dining
- `search_events` - Local events  
- `search_attractions` - Attractions

**Format:**
- Clean Markdown with headings
- Budget-tiered options
- [Book](link) not raw URLs
- Reference previous choices when helpful
""",
)


@travel_agent.tool
async def flight_search_tool(
    ctx: RunContext[TravelDependencies],
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str = "",
) -> str:
    """Search for flights between two cities."""
    prompt = (
        f"Search for flights from {origin} to {destination} departing {departure_date}"
    )
    if return_date:
        prompt += f" returning {return_date}"

    result = await flight_agent.run(prompt, deps=ctx.deps)
    return result.output


@travel_agent.tool
async def hotel_search_tool(
    ctx: RunContext[TravelDependencies],
    city: str,
    checkin_date: str,
    checkout_date: str,
    adults: int = 2,
    rooms: int = 1,
    min_price: int = 0,
    max_price: int = 1000,
) -> str:
    """Search for hotels in a given city and date range."""
    prompt = f"Search for hotels in {city} from {checkin_date} to {checkout_date}"
    if adults > 1:
        prompt += f" for {adults} adults"
    if rooms > 1:
        prompt += f" in {rooms} rooms"
    if min_price > 0 or max_price < 1000:
        prompt += f" between ${min_price} and ${max_price}"

    result = await hotel_agent.run(prompt, deps=ctx.deps)
    return result.output


@travel_agent.tool
async def search_restaurants(
    ctx: RunContext[TravelDependencies],
    city: str,
    limit: int = 10,
) -> str:
    """Find restaurants for a given city."""
    prompt = f"Search for restaurants in {city}"
    if limit != 10:
        prompt += f" (limit {limit})"

    result = await web_agent.run(prompt, deps=ctx.deps)
    return result.output


@travel_agent.tool
async def search_events(
    ctx: RunContext[TravelDependencies],
    city: str,
    user_start_date: str,
    user_end_date: str,
    limit: int = 8,
) -> str:
    """Search live events for travel itinerary."""
    prompt = f"Search for events in {city} from {user_start_date} to {user_end_date}"
    if limit != 8:
        prompt += f" (limit {limit})"

    result = await web_agent.run(prompt, deps=ctx.deps)
    return result.output


@travel_agent.tool
async def search_attractions(
    ctx: RunContext[TravelDependencies],
    city: str,
) -> str:
    """Return a curated set of attractions for a city."""
    prompt = f"Search for attractions in {city}"

    result = await web_agent.run(prompt, deps=ctx.deps)
    return result.output


if __name__ == "__main__":
    import asyncio

    from agent_dependencies import TravelDependencies

    async def test_agent():
        deps = TravelDependencies.from_env()
        result = await travel_agent.run(
            "Hello! Can you help me plan a trip to New York?", deps=deps
        )
        print(result.output)

    asyncio.run(test_agent())
