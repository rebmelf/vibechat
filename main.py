import chainlit as cl
from dotenv import load_dotenv
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers import SelfQueryRetriever
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langfuse import Langfuse
from langfuse.model import TextPromptClient


@cl.on_chat_start
async def start_chatbot():
    llm = ChatOpenAI(model="gpt-4o-mini")
    langfuse = Langfuse()
    system_prompt = langfuse.get_prompt("vibechat_system_prompt")
    cl.user_session.set("llm", llm)
    cl.user_session.set("rag_retriever", create_rag_retriever(llm))
    cl.user_session.set("system_prompt", system_prompt)


@cl.on_message
async def on_message(message: cl.Message):
    llm = cl.user_session.get("llm")  # type: ChatOpenAI
    msg = cl.Message(content="")
    async for chunk in llm.astream(
            compile_prompt_with_retrieved_data(message.content),
            config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk.content)

    await msg.send()


def create_rag_retriever(llm: ChatOpenAI) -> SelfQueryRetriever:
    vector_store = PineconeVectorStore(
        index_name="vibechat",
        embedding=OpenAIEmbeddings(model="text-embedding-3-large")
    )
    document_content_description = "The manual of the car Opel Ampera"
    metadata_field_info = [
        AttributeInfo(
            name="car_type",
            description="Type of the car you should check the manual of",
            type="string"
        )
    ]
    return SelfQueryRetriever.from_llm(
        llm=llm,
        vectorstore=vector_store,
        document_contents=document_content_description,
        metadata_field_info=metadata_field_info
    )


def compile_prompt_with_retrieved_data(question: str):
    rag_retriever = cl.user_session.get("rag_retriever")  # type: SelfQueryRetriever
    system_prompt = cl.user_session.get("system_prompt")  # type:  TextPromptClient
    results = format_docs(rag_retriever.invoke(question))
    return system_prompt.compile(context=results, question=question)


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def main():
    load_dotenv()
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)


if __name__ == "__main__":
    main()
