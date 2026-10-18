from dotenv import load_dotenv
load_dotenv()
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain.tools import tool 
from langchain_core.messages import HumanMessage, ToolMessage
# from langchain_core.output_parsers import StrOutputParser
# from langchain_community.tools.tavily_search import TavilySearchResults
# from rich import print 



llm = ChatGroq(model="openai/gpt-oss-120b")
# search_tool = TavilySearchResults(max_result = 5)

message=[]
#1 creating a tool 
@tool
def get_text_len(text : str)->int:
    """return the number of character in the given string """
    return len(text)

tools = {
    "get_text_len" : get_text_len
}

llm=llm.bind_tools([get_text_len])

# print("you : ")

query=input("you : ")
message.append(HumanMessage(content=query))

# 1st llm call
response= llm.invoke(message)
message.append(response)

if(response.tool_calls):
    name=response.tool_calls[0]['name']
    answer=tools[name].invoke(response.tool_calls[0])
    message.append(answer)

# 2nd llm call , now it have question and tool awerer, and it reframe it in answer
result=llm.invoke(message)

print(result.content)
