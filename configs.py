from dotenv import load_dotenv, dotenv_values
from openai import AsyncOpenAI, OpenAI
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

load_dotenv()

config = dotenv_values(".env")

TEMPERATURE = 0.2

ocr_model = config['OCR_MODEL']
main_model = config['MAIN_MODEL']

async_client = AsyncOpenAI(
    base_url=config['BASE_URL'],
    api_key=config['API_KEY'],
)

client = OpenAI(
    base_url=config['BASE_URL'],
    api_key=config['API_KEY'],
)

qdrant_client = QdrantClient(
    url=config['QDRANT_URL'],
    # api_key=config['QDRANT_API_KEY']
)

embeddings = SentenceTransformer("BAAI/bge-m3")

async def openai_api(messages) -> str: 

    response =  await async_client.chat.completions.create(
        model=ocr_model,
        messages=messages,
    )

    return response.choices[0].message.content

def sync_openai_api(messages) -> str: 

    response = client.chat.completions.create(
        model=main_model,
        messages=messages,
    )

    return response.choices[0].message.content