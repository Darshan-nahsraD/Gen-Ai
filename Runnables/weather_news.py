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

llm=llm.bind_tools([get_news, get_weather])

tooldic = {
    "get_weather" : get_weather,
    "get_news" : get_news
}



print("type exit to quit ")
while True : 
    query= input("you : ")
    if(query== "exit") : break

    messages.append(HumanMessage(content=query))
    response=llm.invoke(messages)
    messages.append(response)

    if response.tool_calls :
        for tools in response.tool_calls :
            name=tools["name"]
            keyword= tooldic[name]

            permission=input(f"llm want to use {name} give permission 'yes/no' : ")

            if permission.strip().lower() == "yes":
                result = keyword.invoke(tools)
            else:
                result = "Tool call denied by user."

            messages.append(
                ToolMessage(content=str(result), tool_call_id=tools["id"])
            )
            
        finalresult=llm.invoke(messages)  
        messages.append(finalresult)
        print(finalresult.content) 
    else :
        print(response.content)  
