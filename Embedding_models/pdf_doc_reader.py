from dotenv import load_dotenv
load_dotenv()
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import WebBaseLoader

docs= TextLoader("RAG/text.txt")
pdf= TextLoader("RAG/btp.pdf")
web= TextLoader("https://www.langchain.com/")

# if you want multiple website , make list and upload all the url

# print(data)
ans1=docs.load()
ans2=pdf.load()
ans3=web.load()

print()
