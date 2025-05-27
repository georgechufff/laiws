import os

import edoc

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

from typing import Iterator

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
