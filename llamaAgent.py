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
        retriever_mode='simple', 
        response_mode='tree_summarize', 
        service_context=service_context
    )

    query_engine_decompose = graph.as_query_engine(
        custom_query_engines=custom_query_engines,
    )

    prompt = f"""
        Reproducibility is a fundamental aspect of scientific research, ensuring that the results, findings, and methodologies
        presented in a paper can be independently validated and verified. You need to act like a Research Engineer in the 
        field of mechanical and aerospace engineering. Part of your role involves assessing the reproducibility of academic
        papers and assess their effectiveness in addressing specific engineering challenges. 

        You are given two PDFs, Paper A and Paper B. Paper A is the original paper, which is delimited by triple backticks. Paper B is a
        paper that cites Paper A. Your task is to check if Paper B reproduces the results of Paper A.

        To analyze the reproducibility of Paper A based on the citations and content in Paper B, follow these directions:
        
        1. Examine Paper B citations. Look for indications of whether Paper B attempted to reproduce the results 
        of Paper A or if it simply cited Paper A as a reference without attempting reproduction.
        2. If Paper B states or implies that it reproduced Paper A's results, carefully scrutinize the corresponding sections or 
        code snippets in Paper B. Compare the reported results in Paper A with those in Paper B to verify if they align.
        3. Note any discrepancies or differences in the reproduced results between Paper A and Paper B. If Paper B successfully 
        reproduces Paper A's results, clearly state that the reproduction was successful. On the other hand, if Paper B produces 
        results that directly contradict or deviate significantly from Paper A's results, explicitly mention the discrepancies
        and highlight that Paper B's results do not align with Paper A's findings.
        4. Provide a detailed analysis of the similarities or differences between Paper A and Paper B, specifically in terms of the
        reproduced results. Explain any modifications, variations, or potential reasons for the discrepancies, if applicable.

        Based on this assessment, give it a score between 0 and 10, where 0 indicates that Paper B does not reproduce Paper A's results
        at all, and 10 indicates that Paper B reproduces Paper A's results perfectly.
        """

    query_engine = index.as_query_engine()
    response = query_engine.query(prompt)
    print(response)

    return 0

if __name__ == "__main__":
    llamaAgent("pdfA.pdf", "pdfB.pdf")