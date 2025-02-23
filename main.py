import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import ChatOllama
from langchain import hub
from dotenv import load_dotenv
import warnings
from prompts import TRANSLATION_PROMPT, INTRODUCTION_PROMPT

if not load_dotenv():
    raise FileNotFoundError("File '.env' does not exist or is empty.")

embeddings = HuggingFaceEmbeddings(
    model_name="intfloat/multilingual-e5-large"
)

try:
    vector_store = FAISS.load_local(
        "faiss_index", embeddings, allow_dangerous_deserialization=True
    )
except:
    warnings.warn("FAISS Database seems to not exist. Trying to recover it manually.")
    from db_creating import vector_store

llm = ChatOllama(model="deepseek-v2:16b", temperature=0.5) 
prompt = hub.pull("rlm/rag-prompt")
print(prompt)
runnable = llm | prompt

st.title("LAIS")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": INTRODUCTION_PROMPT}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Введите Ваше сообщение."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        query = st.session_state.messages[-1]['content']
        content = vector_store.similarity_search_with_score(query)
        docs_content = "\n\n".join(doc.page_content for doc in content)
        answer = runnable.invoke({"question": query, "context": docs_content})
        response = st.write_stream([s + ' ' for s in answer.split()])

    st.session_state.messages.append({"role": "assistant", "content": response})
