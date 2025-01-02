import os

import chainlit as cl
from dotenv import load_dotenv
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers import SelfQueryRetriever
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig, RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone


@cl.on_chat_start
async def start_chatbot():
    llm = ChatOpenAI(model="gpt-4o-mini")
    document_content_description = "The manual of the car Opel Ampera"
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
    vector_store = PineconeVectorStore(index_name="vibechat", embedding=embeddings)
    metadata_field_info = [
        AttributeInfo(
            name="car_type",
            description="Type of the car you should check the manual of",
            type="string"
        )
    ]
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                I would like you to take on the following role. You have access to the Opel Ampera User Manual through a RAG pipeline.
                Based on the data retrieved from it, answer the questions asked. If the answer cannot be found in the manual, respond with an answer that indicates you cannot answer the question.

                Answer as if you were the car itself, speaking directly to your driver. The buttons and the knobs are yours, talk about them as they are your parts. 
                You should talk like a rock star!
                """

            ),
            ("human", "{context}"),
            ("human", "{question}")
        ]
    )
    retriever = SelfQueryRetriever.from_llm(
        llm=llm,
        vectorstore=vector_store,
        document_contents=document_content_description,
        metadata_field_info=metadata_field_info
    )

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    runnable = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
    )
    cl.user_session.set("runnable", runnable)


@cl.on_message
async def on_message(message: cl.Message):
    runnable = cl.user_session.get("runnable")  # type: Runnable
    msg = cl.Message(content="")
    async for chunk in runnable.astream(
            {"question": message.content},
            config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk)

    await msg.send()


def main():
    load_dotenv()
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)


if __name__ == "__main__":
    main()
