import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from datasets import load_dataset
from uuid import uuid4
from tqdm import tqdm

embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-large")
index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))

vector_store = FAISS(
    embedding_function=embeddings,
    index=index,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={},
)

docs = []

law_dataset = load_dataset('csv', data_files='entire_dataset.csv')['train']

count = 0

for law in tqdm(law_dataset):
    if count == 25:
        break
    docs.append(
        Document(
            page_content=law['article'],
            metadata={'source': law['metadata']},
        )
    )
    count += 1

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
all_splits = text_splitter.split_documents(docs)
uuids = [str(uuid4()) for _ in range(len(all_splits))]

vector_store.add_documents(documents=all_splits, ids=uuids)
vector_store.save_local("faiss_index")