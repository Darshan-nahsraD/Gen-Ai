from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.retrievers.multi_query import MultiQueryRetriever
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage

load_dotenv()
# ------------------------------------FULL PROJECT WITH HISTORY , SPILITTER---------------------------------------------------------

embedding= HuggingFaceEmbeddings(
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
)

history = [

]

llm = ChatGroq(model="openai/gpt-oss-120b")

loader = PyPDFLoader("RAG/btp.pdf")

data= loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)


chunks = text_splitter.split_documents(data)

vectorstore = Chroma.from_documents(
    documents=chunks,
    persist_directory= "chroma_db",
    embedding= embedding
)

retriever = vectorstore.as_retriever(
    search_type = "mmr",
    search_kwargs = {
        "k" : 4,
        "fetch_k":10,
        "lambda_mult" :0.5
    }
)

multi_query_retriever = MultiQueryRetriever.from_llm(
    retriever=retriever,
    llm=llm
)


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a helpful AI assistant.

            Use ONLY the provided context to answer the question.

            If the answer is not present in the context,
            say: "I could not find the answer in the document."
            """
        ),
        (
            "human",
            """ Context  : {context}
                Question : {question}
            """
        )
    ]
)
print("press '0' to exit")

# question =input("you : ")

while True:
    query = input("You : ")
    if query == "0":
        break 
    # this line search the relevent top k information from the croma-db and put in docs in the form of list
    docs = MultiQueryRetriever.invoke(query)

    # this make a list of only pagecontent
    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )
    
    final_prompt = prompt.invoke({
        "context" :context,
        "question": query
    })
    
    response = llm.invoke(final_prompt)

    print(f"\n AI: {response.content}")

    history.append(HumanMessage(content=query))
    history.append(AIMessage(content=response.content))


    