from dotenv import load_dotenv
load_dotenv()
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",
    # With the `text-embedding-3` class
    # of models, you can specify the size
    # of the embeddings you want returned.
    # dimensions=1024
)
vector = embeddings.embed_query("hey how are you ?")
print(vector)