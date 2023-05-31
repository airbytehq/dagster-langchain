from langchain import OpenAI
from langchain.vectorstores import VectorStore
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
import pickle

# Update on change
vectorstore_file = "vectorstore.pkl"

with open(vectorstore_file, "rb") as f:
    global vectorstore
    local_vectorstore: VectorStore = pickle.load(f)


qa = RetrievalQA.from_chain_type(llm=OpenAI(temperature=0), chain_type="stuff", retriever=local_vectorstore.as_retriever())

print("Chat Langchain Demo")
print("Ask a question to begin:")
while True:
    query = input("")
    answer = qa.run(query)
    print(answer)
    print("\nWhat else can I help you with:")
