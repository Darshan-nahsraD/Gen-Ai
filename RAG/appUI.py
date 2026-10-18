
import os
import tempfile

import streamlit as st
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
)

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate


# -------------------- CONFIGURATION --------------------

load_dotenv()

st.set_page_config(
    page_title="Document RAG Chatbot",
    page_icon="📚",
    layout="wide",
)

st.title("📚 Chat with Your Documents")
st.caption("Upload documents and ask questions about their content.")


# -------------------- MODELS --------------------

@st.cache_resource
def get_embedding_model():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


@st.cache_resource
def get_llm():
    return ChatGroq(
        model="openai/gpt-oss-120b"
    )


embedding_model = get_embedding_model()
llm = get_llm()


# -------------------- PROMPT --------------------

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a helpful AI assistant.

Use ONLY the provided context to answer the question.

If the answer is not present in the context,
say: "I could not find the answer in the document."

Do not make up facts.
"""
    ),
    (
        "human",
        """Context:
{context}

Question:
{question}
"""
    ),
])


# -------------------- SESSION STATE --------------------

if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# -------------------- DOCUMENT UPLOAD --------------------

st.sidebar.header("📂 Upload Documents")

uploaded_files = st.sidebar.file_uploader(
    "Choose your documents",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True,
)

if st.sidebar.button("Process Documents", type="primary"):

    if not uploaded_files:
        st.sidebar.warning("Please upload at least one document.")

    else:
        all_documents = []

        progress = st.sidebar.progress(0)
        status = st.sidebar.empty()

        for index, uploaded_file in enumerate(uploaded_files):

            status.write(f"Loading {uploaded_file.name}...")

            suffix = os.path.splitext(uploaded_file.name)[1].lower()

            # Save the uploaded file temporarily because
            # LangChain document loaders accept file paths.
            temp_path = None

            try:
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=suffix
                ) as temp_file:

                    temp_file.write(uploaded_file.getvalue())
                    temp_path = temp_file.name

                if suffix == ".pdf":
                    loader = PyPDFLoader(temp_path)

                elif suffix == ".docx":
                    loader = Docx2txtLoader(temp_path)

                elif suffix == ".txt":
                    loader = TextLoader(
                        temp_path,
                        encoding="utf-8"
                    )

                else:
                    continue

                documents = loader.load()

                # Keep the original filename in metadata.
                for document in documents:
                    document.metadata["source"] = uploaded_file.name

                all_documents.extend(documents)

            except Exception as error:
                st.sidebar.error(
                    f"Could not load {uploaded_file.name}: {error}"
                )

            finally:
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)

            progress.progress(
                (index + 1) / len(uploaded_files)
            )

        if all_documents:

            status.write("Splitting documents into chunks...")

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
            )

            chunks = text_splitter.split_documents(all_documents)

            if chunks:
                status.write("Creating embeddings and Chroma database...")

                try:
                    # Build a fresh in-memory vector store.
                    new_vectorstore = Chroma.from_documents(
                        documents=chunks,
                        embedding=embedding_model,
                    )

                    st.session_state.vectorstore = new_vectorstore
                    st.session_state.chat_history = []

                    status.success(
                        f"Processed {len(uploaded_files)} uploaded files "
                        f"into {len(chunks)} chunks."
                    )

                except Exception as error:
                    status.empty()
                    st.sidebar.error(
                        f"Could not create the vector database: {error}"
                    )

            else:
                status.error("No text could be extracted from the files.")

        else:
            status.error("No documents could be loaded.")


# -------------------- CHAT INTERFACE --------------------

if st.session_state.vectorstore is None:

    st.info(
        "👈 Upload your PDF, DOCX, or TXT files in the sidebar, "
        "then click **Process Documents** to start chatting."
    )

else:

    st.success("Documents are ready! Ask your first question below.")

    # Display existing chat messages.
    for message in st.session_state.chat_history:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    query = st.chat_input("Ask a question about your documents...")

    if query:

        # Display the user's question.
        with st.chat_message("user"):
            st.markdown(query)

        st.session_state.chat_history.append({
            "role": "user",
            "content": query,
        })

        with st.chat_message("assistant"):

            with st.spinner("Searching documents and generating answer..."):

                try:
                    retriever = st.session_state.vectorstore.as_retriever(
                        search_type="mmr",
                        search_kwargs={
                            "k": 4,
                            "fetch_k": 10,
                            "lambda_mult": 0.5,
                        },
                    )

                    # Retrieve relevant document chunks.
                    docs = retriever.invoke(query)

                    # Combine the retrieved text.
                    context = "\n\n".join(
                        doc.page_content for doc in docs
                    )

                    # Generate the answer.
                    final_prompt = prompt.invoke({
                        "context": context,
                        "question": query,
                    })

                    response = llm.invoke(final_prompt)
                    answer = response.content

                    st.markdown(answer)

                    # Show sources used for the answer.
                    with st.expander("View retrieved sources"):
                        if docs:
                            for i, doc in enumerate(docs, start=1):
                                source = doc.metadata.get(
                                    "source",
                                    "Unknown source"
                                )

                                st.markdown(
                                    f"**Source {i}: {source}**"
                                )
                                st.write(doc.page_content)
                        else:
                            st.write("No relevant chunks were retrieved.")

                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": answer,
                    })

                except Exception as error:
                    st.error(f"Something went wrong: {error}")
