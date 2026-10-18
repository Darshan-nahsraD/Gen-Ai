from dotenv import load_dotenv
load_dotenv()
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

llm = HuggingFaceEndpoint(
    repo_id="deepseek-ai/DeepSeek-R1",
)
model = ChatHuggingFace(llm=llm)

response= model.invoke("hell, how do you do")
print(response.content)