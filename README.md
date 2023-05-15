# Airbyte - Dagster - Langchain demo

To run, you need python 3 and docker installed:
* [Start Airbyte locally](https://github.com/airbytehq/airbyte#quick-start)
* Set up connection
* Install requirements via `pip install -r requirements.txt`
* Run `dagster dev -f ingest.py` to start the ingest pipeline
* Go to `http://127.0.0.1:3000/asset-groups` to see the Dagster UI and materialize all steps
* Run `EXPORT OPENAI_API_KEY={YOUR_API_KEY}; python query.py` to start the QA interface
* Ask questions: "How much is a Volkswagen?"
