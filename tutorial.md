# Making data available to langchain using Airbyte and Dagster

Building useful software with LLMs requires access to relevant data in most cases.
Airbyte can provide access to the data, dagster can orchestrate the process of bringing it into shape for langchain, which can leverage the actual LLM.

This tutorial explains step by step how to set up a pipeline that brings data from a public API into a format that can be used by langchain.

To run, you need python 3 and docker installed:

The start airbyte locally like described on https://github.com/airbytehq/airbyte#quick-start 

Set up a connection:
COnfigure source (in this case "Faker")
Configure local json destination with path /local
Configure a connection from the faker source to local json destination (manual run - dagster will take are of that)


Configure the software defined assets for dagster in `ingest.py`:

First, load the assets from airbyte (no need to define manually):
```
airbyte_instance = AirbyteResource(
    host="localhost",
    port="8000",
)

airbyte_assets = load_assets_from_airbyte_instance(
    airbyte_instance,
    key_prefix="airbyte_asset",
)

```


Then, add the langchain loader to turn the raw jsonl file into langchain documents:
```
# Airbyte loader
airbyte_loader = AirbyteJSONLoader(
    "/tmp/airbyte_local/local_json/products/_airbyte_raw_products.jsonl"
)


@asset(
    name="raw_documents",
    ins={
        "airbyte_data": AssetIn(
            asset_key=["airbyte_asset", "products"], input_manager_key="airbyte_io_manager"
        )
    },
)
def raw_documents(airbyte_data):
    """Load the raw document text from the source."""
    return airbyte_loader.load()
```


Then, split the documents up into chunks so they will fit the LLM context later:
```
def split_documents(
    documents: List[Document], text_splitter: TextSplitter
) -> List[Document]:
    return text_splitter.split_documents(documents)

@asset(
    name="documents",
    ins={"raw_documents": AssetIn("raw_documents")},
    compute_kind="langchain",
)
def documents(raw_documents):
    """Split the documents into chunks that fit in the LLM context window."""
    return split_documents(raw_documents, RecursiveCharacterTextSplitter(chunk_size=1000))
```


Then, generate the embeddings for the documents:
```
def create_embeddings_vectorstore(
    documents: List[Document], embeddings: Embeddings, vectorstorecls: VectorStore
):
    return vectorstorecls.from_documents(documents, embeddings)

@asset(
    name="vectorstore",
    io_manager_key="vectorstore_io_manager",
    freshness_policy=FreshnessPolicy(maximum_lag_minutes=5, cron_schedule="@daily"),
    ins={"documents": AssetIn("documents")},
    compute_kind="vectorstore",
)
def vectorstore(documents):
    """Compute embeddings and create a vector store."""
    return create_embeddings_vectorstore(documents, OpenAIEmbeddings(), FAISS)
```


Finally, define how to manage IO and export the definitions for dagster:
```
class VectorstoreIOManager(IOManager):
    def load_input(self, context):
        raise NotImplementedError()

    def handle_output(self, context, obj):
        filename = save_vectorstore_to_disk(context.step_key, obj)
        context.add_output_metadata({"filename": filename})


class AirbyteIOManager(IOManager):
    def load_input(self, context):
        return context.upstream_output.metadata

    def handle_output(self, context, obj):
        raise NotImplementedError()


# Defs to output
# Local vectorstore
defs = Definitions(
    assets=[airbyte_assets, raw_documents, documents, vectorstore],
    resources={
        "vectorstore_io_manager": VectorstoreIOManager(),
        "airbyte_io_manager": AirbyteIOManager(),
    },
    sensors=[
        build_asset_reconciliation_sensor(
            AssetSelection.all(),
            name="reconciliation_sensor",
        )
    ],
)
```

See the full ingest.py file here: [LINK]

Now, we can run the pipeline:
Run `dagster dev -f ingest.py` to start the ingest pipeline
Go to `http://127.0.0.1:3000/asset-groups` to see the Dagster UI and materialize all steps

Now, a `vectorstore.pkl` file showed up - this contains the embeddings for the data we just loaded via Airbyte. The next step is to put it to work by running a QA chain using LLMs:

Create a new file `query.py`:

Load the embeddings:
```
vectorstore_file = "vectorstore_vectorstore.pkl"

with open(vectorstore_file, "rb") as f:
    global vectorstore
    local_vectorstore: VectorStore = pickle.load(f)
```

Initialize LLM and QA tool based on the vectorstore:
```
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
```


Add a question-answering loop:
```
print("Chat Langchain Demo")
print("Ask a question to begin:")
while True:
    query = input("")
    answer = qa.run(query)
    print(answer)
    print("\nWhat else can I help you with:")
```

See the full query.py file here: [LINK]

You can run it with `OPENAI_API_KEY=YOUR_API_KEY python query.py`

Of course this is just a simplistic demo, but it showcases how to use Airbyte and Dagster to bring data into a format that can be used by langchain.