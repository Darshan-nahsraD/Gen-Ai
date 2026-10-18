from dotenv import load_dotenv
load_dotenv()
import os
import requests
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain.tools import tool 
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from tavily import TavilyClient
from langchain.agents import create_agent 
from langchain.agents.middleware import wrap_tool_call
# from langchain_core.output_parsers import StrOutputParser
# from rich import print 

llm = ChatGroq(model="openai/gpt-oss-120b")

messages=[]


@tool
def get_news(topic: str, city: str = "") -> str:
    """Get the latest news about a specific topic, optionally limited to a city or location."""

    if city:
        search_query = f"latest {topic} news in {city}"
    else:
        search_query = f"latest news about {topic}"

    response = tavily_client.search(
        query=search_query,
        search_depth="basic",
        max_results=5
    )

    results = response.get("results", [])

    if not results:
        return f"No news found for topic: {topic}"

    news_list = []

    for r in results:
        title = r.get("title", "No title")
        url = r.get("url", "")
        snippet = r.get("content", "")

        news_list.append(
            f"- {title}\n"
            f"  Link: {url}\n"
            f"  Summary: {snippet[:150]}..."
        )

    return (
        f"Latest news about {topic}"
        + (f" in {city}" if city else "")
        + ":\n\n"
        + "\n\n".join(news_list)
    )

@tool
def get_weather(city : str) ->str:
    """give the weather of the city"""
    
    api_key = os.getenv("OPENWEATHER_API_KEY")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city},IN&appid={api_key}&units=metric"
    
    response = requests.get(url)
    data = response.json()
    
    if str(data.get("cod")) != "200":
        return f"Error: {data.get('message', 'Could not fetch weather')}"
    
    temp = data["main"]["temp"]
    desc = data["weather"][0]["description"]
    
    return f"Weather in {city}: {desc}, {temp}°C"


tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# @tool
# def get_news(city: str) -> str:
#     """Get latest news about a city"""
    
#     response = tavily_client.search(
#         query=f"latest news in {city}",
#         search_depth="basic",
#         max_results=3
#     )
    
#     results = response.get("results", [])
    
#     if not results:
#         return f"No news found for {city}"
    
#     news_list = []
    
#     for r in results:
#         title = r.get("title", "No title")
#         url = r.get("url", "")
#         snippet = r.get("content", "")
        
#         news_list.append(
#             f"- {title}\n  🔗 {url}\n  📝 {snippet[:100]}..."
#         )
    
#     return f"Latest news in {city}:\n\n" + "\n\n".join(news_list)

@wrap_tool_call
def human_approval(request, handler):
    """Ask for human approval before every tool call."""
    tool_name = request.tool_call["name"]
    confirm = input(f"Agent wants to call '{tool_name}'. Approve? (yes/no): ")

    if confirm.lower() != "yes":
        return ToolMessage(
            content="Tool call denied by user.",
            tool_call_id=request.tool_call["id"]
        )

    return handler(request)  

agent = create_agent(
    llm,
    tools = [get_weather,get_news],
    system_prompt= "you are a helpful city assistant.",
    middleware= [human_approval]
)

print("City Agent | type exit to quit")

while True:
    user_input = input("You : ")
    if user_input.lower() == "exit":
        break 
    result = agent.invoke({
        "messages":[{"role": "user", "content": user_input}]
    })

    print("bot : ", result['messages'][-1].content )