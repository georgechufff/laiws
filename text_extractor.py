import asyncio
import base64
from dotenv import load_dotenv, dotenv_values
import edoc
from io import BytesIO
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document

from langchain_community.document_loaders import (
    BSHTMLLoader,
    CSVLoader,
    Docx2txtLoader,
    PyPDFLoader,
    TextLoader,
    UnstructuredExcelLoader,
    UnstructuredPowerPointLoader,
)

from openai import AsyncOpenAI
import os
from PIL import Image
from prompts import LLM_OCR_PROMPT
import traceback
from typing import Iterator
from configs import openai_api

class DocLoader(BaseLoader):
    """An example document loader that reads a file line by line."""

    def __init__(self, file_path: str) -> None:
        """Initialize the loader with a file path.

        Args:
            file_path: The path to the file to load.
        """
        self.file_path = file_path

    def load(self) -> Iterator[Document]:
        return Document(
            page_content=edoc.extraxt_txt(self.file_path),
            metadata={"source": self.file_path},
        )


def encode_image(image: Image.Image) -> str:
    """Кодирует изображение в base64.

    Args:
        image (Image.Image): Изображение для кодирования.

    Returns:
        str: Закодированное изображение в формате base64.
    """
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


async def llm_ocr(file_path):
    """Выполняет OCR с использованием LLM.

    Returns:
        str: Распознанный текст.
    """

    image = Image.open(file_path)

    n = 1 # Количество частей, на которые делится изображение (по умолчанию 1)

    segments_tasks = []
    
    # for image in images:
    width, height = image.size
    part_height = height
    # Если ширина изображения больше, чем высота, добавляем белые поля для квадратного формата
    if width > height:
        size = max(width, height)
        new_img = Image.new("RGB", (size, size), (255, 255, 255))
        new_img.paste(image, ((size - width) // 2, (size - height) // 2))
        image = new_img
    # Если высота изображения больше, чем ширина, делим его на 3 части (самое оптимальное по скорость/качество)
    elif width < height:
        n = 3
        part_height = height // n

    # Обрабатываем каждую часть изображения
    for i in range(n):
        top = i * part_height
        bottom = (i + 1) * part_height if i < n - 1 else image.size[1]

        try:
            def crop_image(image, top, bottom):
                width, _ = image.size
                cropped_img = image.crop((0, top, width, bottom))
                return cropped_img

            cropped_img = await asyncio.to_thread(crop_image, image, top, bottom)
            openai_img_schema = {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{encode_image(cropped_img)}",
                    "detail": "low"
                }
            }

            messages = [
                {
                    "role": "user",
                    "content": [
                        openai_img_schema, 
                        {"type": "text", "text": LLM_OCR_PROMPT}
                    ]
                }
            ]

            segments_tasks.append(asyncio.create_task(openai_api(messages)))

        except Exception as e:
            traceback.format_exc()
            continue

    results = await asyncio.gather(*segments_tasks)
    return ''.join(results)

class ImageLoader(BaseLoader):
    """An example document loader that reads a file line by line."""

    def __init__(self, file_path: str) -> None:
        """Initialize the loader with a file path.

        Args:
            file_path: The path to the file to load.
        """
        self.file_path = file_path

    def load(self) -> Iterator[Document]:
        
        result = asyncio.run(llm_ocr(self.file_path))

        return [Document(
            page_content=result,
            metadata={"source": self.file_path},
        )]

class TextExtractor:
    """A class that extracts text from a file and returns it as a string."""

    def __init__(self, file_path):
        """Initialize the text extractor with a file path.

        Args:
            file_path: The path to the file to extract text from.
        """
        self.file_path = file_path
        self.extension = os.path.splitext(self.file_path)[-1].lower()
        self.doc_loader = self._create_loader()
        self.id = None
        self.metadata = None
        self.page_content = None
        self.type = None

    def _create_loader(self):
        """Create a document loader based on the file extension."""
        if self.extension == ".txt":
            return TextLoader(self.file_path, encoding='utf-8')
        elif self.extension == ".csv":
            return CSVLoader(self.file_path)
        elif self.extension == ".docx":
            return Docx2txtLoader(self.file_path)
        elif self.extension == '.doc':
            return DocLoader(self.file_path)
        elif self.extension == ".pdf":
            return PyPDFLoader(self.file_path)
        elif self.extension == ".html":
            return BSHTMLLoader(self.file_path)
        elif self.extension in [".xlsx", ".xls"]:
            return UnstructuredExcelLoader(self.file_path)
        elif self.extension in [".pptx", "ppt"]:
            return UnstructuredPowerPointLoader(self.file_path)
        elif self.extension.lower() in ['.jpg', '.jpeg', '.png']:
            return ImageLoader(self.file_path)

    def load(self):
        """Load the data from the file and return it as a string."""
        data = self.doc_loader.load()[0].model_dump()
        self.id = data.get("id")
        self.metadata = data.get("metadata")
        self.page_content = data.get("page_content")
        self.type = data.get("type")

        result = ''
        if self.metadata:
            result += f"Metadata: {self.metadata}\n"
        if self.type:
            result += f"Document type: {self.type}\n"
        if self.page_content:
            result += f"Content: {self.page_content}\n"

        return result
