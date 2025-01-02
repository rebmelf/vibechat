import os
import time
from typing import List

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec


def load_pdf() -> List[Document]:
    loader = PyPDFLoader(file_path="ampera_en.pdf")
    pages = []
    for page in loader.load():
        page.metadata["car_type"] = "Ampera"
        pages.append(page)
    print(f"{len(pages)} pages loaded")
    return pages


load_dotenv()
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=pinecone_api_key)
existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
index_name = "vibechat"
if index_name not in existing_indexes:
    pc.create_index(
        name=index_name,
        dimension=3072,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )
    while not pc.describe_index(index_name).status["ready"]:
        time.sleep(1)
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
index = pc.Index(index_name)
print(index)
vector_store = PineconeVectorStore.from_existing_index(index_name=index_name, embedding=embeddings)
print("Vector store initiated")
vector_store.add_documents(documents=load_pdf())
print("Documents loaded")
