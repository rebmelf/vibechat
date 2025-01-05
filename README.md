# Vibechat

VibeChat is a chatbot project that lets you chat with car manuals as if you were talking to your car. The goal is to
make it easy to find information in your car's manual by asking simple questions.

Right now, VibeChat uses a hardcoded car manual PDF and shows how tools like OpenAI, Pinecone, LangChain, and Chainlit
can work together. In the future, VibeChat will become more flexible and support different tasks with multi-agent
workflows.

## Features and Functionalities

### Integrations:

- OpenAI API: Leverages OpenAI's powerful API for embedding and querying content.
- Pinecone Vector Database: Uses Pinecone to store and retrieve vectorized representations of data for efficient
  similarity search.

### Functionalities:

- Basic Chatbot UI: A basic chatbot interface is implemented using Chainlit. The interface relies only on
  `on_chat_start` and `on_message` hooks to handle interactions.
- Document embedding script: A standalone script (initialize_pinecone.py) uploads a hardcoded PDF file to the Pinecone
  vector database for use in retrieval tasks.
- OpenAI-Pinecone Workflow: The project includes a simple setup to embed and query the vector database using Langchain.

## Getting Started

### Prerequisites

Ensure you have the following installed:

- Python 3.12 or higher
- Pinecone account, free tier is sufficient (https://www.pinecone.io/)
- Langfuse account, free tier is sufficient (https://www.langfuse.com/)

The project is built with the following libraries:

- Chainlit
- Langchain
- Langgraph

### Installation

1. Clone the repository.
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Set up the environment variables (or use your .env file):

```bash
export OPENAI_API_KEY=<your_openai_api_key>
export PINECONE_API_KEY=<your_pinecone_api_key>
export LANGFUSE_SECRET_KEY=<your_langfuse_api_key>
export LANGFUSE_PUBLIC_KEY=<your_langfuse_public_api_key>
export LANGFUSE_HOST=<your_langfuse_host>
```

4. Run the PDF upload script to initialize the Pinecone database:

```bash
python initialize_pinecone.py
```

5. Run the Chainlit server:

```bash
chainlit run main.py
```

## Current Status

This project currently supports:

- A basic chatbot interface
- Retrieval-Augmented Generation (RAG) with a single embedded PDF
- Fundamental OpenAI and Pinecone integrations
- Lnagfuse integration for prompt management

## Roadmap

Planned improvements include:

- Cleaner codebase with modular components
- Support for multi-agent workflows with distinct functionalities
- Dynamic document upload and management
- Enable more advanced Chainlit features (login, chat history, etc.)

## Changelog

### 05 Jan 2025

- Added LangFuse for prompt management. The free hosted tier is sufficient for now. To use it, create an organization
  and project, then add your keys as the env variables.
- Prompts are now stored in langfuse_prompts.txt, you can add those under <project name>/Prompts in Langfuse. If you
  modify them, make sure, that the version you try to use is tagged with 'Production'.
- Improved readability, although the code is still quite messy.
- The current setup calls the RAG retriever followed by the LLM to generate answers. This will likely change in the
  future, with plans to incorporate LangGraph.

