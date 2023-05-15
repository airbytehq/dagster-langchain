from langchain import OpenAI
from langchain.vectorstores import VectorStore
from langchain.chains import RetrievalQA
from langchain.agents import Tool
from langchain.llms import OpenAI
from langchain.agents import initialize_agent
import pickle
import sys

# Update on change
vectorstore_file = "vectorstore_vectorstore.pkl"

with open(vectorstore_file, "rb") as f:
    global vectorstore
    local_vectorstore: VectorStore = pickle.load(f)


llm = OpenAI(temperature=0)
tools = [
    Tool(
        name="Local Car Shop QA System",
        func=RetrievalQA.from_chain_type(
            llm=llm, chain_type="stuff", retriever=local_vectorstore.as_retriever()
        ).run,
        description="""Useful for when you need to answer questions about cars for sale. 
        Input should be a fully formed question.""",
    )
]

qa = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)

print("Chat Langchain Demo")
print("Ask a question to begin:")
while True:
    query = input("")
    answer = qa.run(query)
    print(answer)
    print("\nWhat else can I help you with:")
