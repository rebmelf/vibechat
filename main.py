from dotenv import load_dotenv

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_openai import ChatOpenAI

import chainlit as cl


@cl.on_chat_start
async def start_chatbot():
    llm = ChatOpenAI(model="gpt-4o-mini")
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful translator, who translates English to Hungarian"
            ),
            ("human", "{sentence}")
        ]
    )
    runnable = prompt | llm | StrOutputParser()
    cl.user_session.set("runnable", runnable)


@cl.on_message
async def on_message(message: cl.Message):
    runnable = cl.user_session.get("runnable")  # type: Runnable

    msg = cl.Message(content="")

    async for chunk in runnable.astream(
        {"sentence": message.content},
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
