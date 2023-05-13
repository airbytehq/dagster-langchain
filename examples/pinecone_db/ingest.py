from dagchain import (
    DagchainPineconeDefinitions,
    DagChainBaseLoader,
)
from langchain.document_loaders import CollegeConfidentialLoader
import sys

if not sys.warnoptions:
    import warnings

    warnings.simplefilter("ignore")
##### Change your loaders as desired ######

# College loader
college_url = "https://www.collegeconfidential.com/colleges/brown-university/"
loader = CollegeConfidentialLoader(college_url)
college_dagchain = DagChainBaseLoader("college", [loader])

# Pinecone vectorstore DB. Currently only supports 1 dagchain.
defs = DagchainPineconeDefinitions("langchain_pinecone", [college_dagchain])
