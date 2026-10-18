# structured pompt proj
from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
llm = ChatGroq(model="openai/gpt-oss-120b")

from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
history = [

]
from pydantic import BaseModel
from typing import Optional, List

class schema(BaseModel):
    title: str 
    release_year : Optional[int]
    genre: List[str]
    director: Optional[str]
    cast: List[str]
    rating: Optional[float]
    summary: str

from langchain_core.output_parsers import PydanticOutputParser
parser = PydanticOutputParser(pydantic_object=schema)

from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "Extract movie information from the paragraph.\n{rules}"),
    ("human", "{paragraph}"),
])

para=input("give your movie paragraph :")

finalquerry= prompt.invoke(
    {"paragraph" : para,
     "rules" : parser.get_format_instructions()
     }

)

response = llm.invoke(finalquerry)
result = parser.parse(response.content)

print(result.model_dump_json(indent=2))
# print(response.content)

history.append(HumanMessage(content=para))
history.append(AIMessage(content=response.content))

