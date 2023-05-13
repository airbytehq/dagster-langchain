from dagster import AssetIn
from dagchain import (
    DagchainDefinitions,
    DagChainBaseLoader,
)
from dagster_airbyte import load_assets_from_airbyte_instance, AirbyteResource
from langchain.document_loaders import CollegeConfidentialLoader, AZLyricsLoader, AirbyteJSONLoader
import sys
import logging

if not sys.warnoptions:
    import warnings

    warnings.simplefilter("ignore")
##### Change your loaders as desired ######

airbyte_instance = AirbyteResource(
    host="localhost",
    port="8000",
)

airbyte_assets = load_assets_from_airbyte_instance(
    airbyte_instance,
    key_prefix="airbyte_asset",
)

# College loader
college_url = "https://www.collegeconfidential.com/colleges/brown-university/"
loader = CollegeConfidentialLoader(college_url)
# college_dagchain = DagChainBaseLoader("college", [loader])

# Music loader
song_url1 = "https://www.azlyrics.com/lyrics/mileycyrus/flowers.html"
song_url2 = "https://www.azlyrics.com/lyrics/taylorswift/teardropsonmyguitar.html"
loader1 = AZLyricsLoader(song_url1)
loader2 = AZLyricsLoader(song_url2)
# music_dagchain = DagChainBaseLoader("music", [loader1, loader2])

for d in airbyte_assets.compute_cacheable_data():
    print(d)

# Airbyte loader
airbyte_loader = AirbyteJSONLoader("/tmp/airbyte_local/test.jsonl/_airbyte_raw_data.jsonl")
airbyte_dagchain = DagChainBaseLoader("airbyte", [airbyte_loader], AssetIn(asset_key=["airbyte_asset","data"],input_manager_key="airbyte_io_manager" ))

# Defs to output
# Local vectorstore
defs = DagchainDefinitions([airbyte_dagchain], additional_assets=[airbyte_assets])


# Pinecone vectorstore DB. Currently only supports 1 dagchain.
# defs = DagchainPineconeDefinitions(
#     "langchain_pinecone", [college_dagchain]
# )
