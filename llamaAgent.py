from llama_index import (
    VectorStoreIndex, 
    SimpleKeywordTableIndex, 
    SimpleDirectoryReader,
    LLMPredictor,
    ServiceContext
)
from langchain.llms.openai import OpenAIChat
from llama_index.indices.composability import ComposableGraph
from llama_index.indices.query.query_transform.base import DecomposeQueryTransform
from llama_index.query_engine.transform_query_engine import TransformQueryEngine
import openai
import os

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) #reads local .env file

# Get value of OPENAI_API_KEY environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")

# Set the API key for the OpenAI API client
openai.api_key = openai_api_key

print("OpenAI API key:", openai.api_key)

def llamaAgent(pdfAPath, pdfBPath):
    pdfs = {}
    pdfs["A"] = SimpleDirectoryReader(input_files=[f"{pdfAPath}"]).load_data()
    pdfs["B"] = SimpleDirectoryReader(input_files=[f"{pdfBPath}"]).load_data()

    llm_predictor_chatgpt = LLMPredictor(llm=OpenAIChat(temperature=0, model_name="gpt-3.5-turbo-16k"))
    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor_chatgpt)

    indices = {}
    descs = {}
    for paper in ["A","B"]:
        indices[paper] = VectorStoreIndex.from_documents(pdfs[paper], service_context=service_context)
        descs[paper] = f"Paper {paper}"

    graph = ComposableGraph.from_indices(
        SimpleKeywordTableIndex,
        [index for _, index in indices.items()], 
        [desc for _, desc in descs.items()],
        max_keywords_per_chunk=50
    )
    decompose_transform = DecomposeQueryTransform(
        llm_predictor_chatgpt, verbose=True
    )

    custom_query_engines = {}
    for index in indices.values():
        query_engine = index.as_query_engine(service_context=service_context)
        transform_extra_info = {'index_summary': index.index_struct.summary}
        tranformed_query_engine = TransformQueryEngine(query_engine, decompose_transform, transform_extra_info=transform_extra_info)
        custom_query_engines[index.index_id] = tranformed_query_engine

    custom_query_engines[graph.root_index.index_id] = graph.root_index.as_query_engine(
        retriever_mode='embedding', 
        response_mode='accumulate', 
        service_context=service_context
    )

    query_engine_decompose = graph.as_query_engine(
        custom_query_engines=custom_query_engines,
    )

    

    prompt = f"""
        How correlated is Paper A with Paper B? You must respond with an integer between 0 to 10.
        """
    response = query_engine_decompose.query(prompt)
    print(response)

    prompt = f"""
        Does Paper B cite Paper A?
        """
    response = query_engine_decompose.query(prompt)
    print(response)

    return 0

if __name__ == "__main__":
    llamaAgent("pdfA.pdf", "pdfB.pdf")