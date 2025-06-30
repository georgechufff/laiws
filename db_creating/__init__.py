# import faiss
# from langchain_community.docstore.in_memory import InMemoryDocstore
# from langchain_community.vectorstores import FAISS
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_core.documents import Document
# from langchain_text_splitters import RecursiveCharacterTextSplitter
from datasets import load_dataset
# from uuid import uuid4
from tqdm import tqdm
from configs import embeddings, qdrant_client
from qdrant_client.models import PointStruct, VectorParams, Distance

docs = []
law_dataset = load_dataset('csv', data_files='db_creating/entire_dataset.csv')['train']

try:
    qdrant_client.create_collection(
        collection_name='laiws',
        vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
    )

except Exception as e:
    pass

count = 0

for law in tqdm(law_dataset):
    docs.append(
        [
            embeddings.encode(law['article']),
            dict(
                page_content=law['article'],
                metadata=law['metadata'],
            )
        ]
    )
    count += 1
    if count % 25 == 0:
        try:
            operation_info = qdrant_client.upsert(
                collection_name="laiws",
                wait=True,
                points=[
                    PointStruct(id=count - 25 + i, vector=d[0], payload=d[1]) for i, d in enumerate(docs)
                ]
            )
        except Exception as e:
            for i, d in enumerate(docs):
                operation_info = qdrant_client.upsert(
                    collection_name="laiws",
                    wait=True,
                    points=[
                        PointStruct(id=count - 25 + i, vector=d[0], payload=d[1])
                    ]
                )
        docs = []
            
            
            

# operation_info = qdrant_client.upsert(
#     collection_name="laiws",
#     wait=True,
#     points=[
#         PointStruct(id=i, vector=d[0], payload=d[1]) for i, d in enumerate(docs)
#     ]
# )

# text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
# all_splits = text_splitter.split_documents(docs)
# uuids = [str(uuid4()) for _ in range(len(all_splits))]

# vector_store.add_documents(documents=all_splits, ids=uuids)
# vector_store.save_local("faiss_index")