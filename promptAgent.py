# /////////////////////////////////SETUP////////////////////////////////////////

from dotenv import load_dotenv
import logging
import sys
import requests
import openai
import os
import re
import PyPDF2 # Function to parse the PDF and extract citations

# import necessary libraries
from io import StringIO
from pdfminer.layout import LAParams
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LTTextBox, LTTextLine
from pdfminer.converter import PDFPageAggregator, TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from dotenv import load_dotenv
from citationTree import CitationTree
from paper_repository import Paper
from utils import createPaperFromDoi, retrieveAbstract


# Load environment variables from .env file
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) #reads local .env file

# Get value of OPENAI_API_KEY environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")

# Set the API key for the OpenAI API client
openai.api_key = openai_api_key

print("OpenAI API key:", openai.api_key)

# function uses the OpenAI API client to generate text based on a prompt using 
def get_completion(prompt, model="gpt-3.5-turbo-16k"):
    # user prompt (initialized as a list)
    # 2 key-value pairs: role (indicates message is from 'user') and content.
    messages = [{"role": "user", "content": prompt}]
    # response from the api call
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        max_tokens=2048,
        temperature=0, # degree of randomness of the model's output
        n = 1 # number of completions to generate for each prompt
    )
    return response.choices[0].message["content"]


def parse_pdf_citations(file_path):
    citations = []
    with open(file_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        num_pages = len(reader.pages)

        for page_number in range(num_pages):
            page = reader.pages[page_number]
            text = page.extract_text()

            citation_pattern = r"\[(\d+)\]"
            matches = re.findall(citation_pattern, text)
            if matches:
                citations.extend([int(match) for match in matches])

    return citations

def calculate_internal_score(citing_paper):
    score = 0

    # Criteria 1: Number of citations
    score += len(citing_paper.cited_by)

    # Criteria 2: Self-citations
    self_citations = [doi for doi in citing_paper.cited_by if doi == citing_paper.doi]
    score -= len(self_citations)

    return score



def check_reproduction(pdfA_path, pdfB_path, indicator, abstract = None): # indicator = True for paper and False for abstract
    output_string = StringIO()
    # Extract the citations from PDF1
    # citation_pos_pdfA = parse_pdf_citations(pdfB_path)
    # print("Citations from PDFB:", citation_pos_pdfA, "\n")
    # with open(pdfA_path, 'rb') as pdfA_file:
    #         parser = PDFParser(pdfA_file)
    #         document = PDFDocument(parser)
    #         parser.set_document(document)
    #         metadata = document.info[0]
    #         title = metadata.get()
    # find the index within these citations that match the title of pdfA
    # for i in range(len(citation_pos_pdfA)):
    #     if citation_pos_pdfA[i] == title:
    #         citation_pos_pdfA = i
    #         break

    if indicator == True:
        # Extract the content of PDF2 for citation analysis
        # with open(pdfB_path, 'rb') as pdfB_file:
        #     parser = PDFParser(pdfB_file)
        #     document = PDFDocument(parser)
        #     parser.set_document(document)
        #     metadata = document.info[0]
        #     title = metadata.get('Title', '')
        #     author = metadata.get('Author', '')
        #     rsrcmgr = PDFResourceManager()
        #     device = PDFPageAggregator(rsrcmgr, laparams=LAParams())
        #     interpreter = PDFPageInterpreter(rsrcmgr, device)

        #     citations_found = []
        #     for page in PDFPage.create_pages(document):
        #         interpreter.process_page(page)
        #         content = output_string.getvalue()
        #         output_string.seek(0)
        #         output_string.truncate(0)
        #         interpreter.process_page(page)
        #         layout = device.get_result()
        #         for element in layout:
        #             if isinstance(element, LTTextBox) or isinstance(element, LTTextLine):
        #                 text = element.get_text().strip()
        #                 # Check if the text contains any citations from PDF1
        #                 # for citation in citation_pos_pdfA:
        #                 #     # if f"[{citation}]" in text: 
        #                 citations_found.append(text)
            output_string = StringIO()
            with open(pdfB_path, 'rb') as pdfB_file:
                resource_manager = PDFResourceManager()
                device = TextConverter(resource_manager, output_string, laparams=LAParams())
                interpreter = PDFPageInterpreter(resource_manager, device)
                parser = PDFParser(pdfB_file)
                document = PDFDocument(parser)
                metadata = document.info[0]
                title = metadata.get('Title', '')
                author = metadata.get('Author', '')
                for page_number, page in enumerate(PDFPage.get_pages(pdfB_file, maxpages=0, caching=True, check_extractable=True), start=1):
                    interpreter.process_page(page)
                    pdfB_page = output_string.getvalue()
                    output_string.seek(0)
                    output_string.truncate(0)
                    # Send prompt to OpenAI API to check if PDF2 reproduces the results of PDF1
                    prompt = f"""
                    Reproducibility is a fundamental aspect of scientific research, ensuring that the results, findings, and methodologies
                    presented in a paper can be independently validated and verified. You need to act like a Research Engineer in the 
                    field of mechanical and aerospace engineering. Part of your role involves assessing the reproducibility of academic
                    papers and assess their effectiveness in addressing specific engineering challenges. 

                    You are given two PDFs, PDFA and PDFB. PDFA is the original paper, which is delimited by triple backticks. PDFB is a
                    paper that cites PDFA. You are given the relevant pages within PDFB that cite and utilize PDFA i.e. PDFB citations,
                    which is delimited by double backticks. Your task is to check if PDFB reproduces the results of PDFA.

                    To analyze the reproducibility of PDFA based on the citations and content in PDFB, follow these directions:
                    
                    1. Examine PDFB citations. Look for indications of whether PDFB attempted to reproduce the results 
                    of PDFA or if it simply cited PDFA as a reference without attempting reproduction.
                    2. If PDFB states or implies that it reproduced PDFA's results, carefully scrutinize the corresponding sections or 
                    code snippets in PDFB. Compare the reported results in PDFA with those in PDFB to verify if they align.
                    3. Note any discrepancies or differences in the reproduced results between PDFA and PDFB. If PDFB successfully 
                    reproduces PDFA's results, clearly state that the reproduction was successful. On the other hand, if PDFB produces 
                    results that directly contradict or deviate significantly from PDFA's results, explicitly mention the discrepancies
                    and highlight that PDFB's results do not align with PDFA's findings.
                    4. Provide a detailed analysis of the similarities or differences between PDFA and PDFB, specifically in terms of the
                    reproduced results. Explain any modifications, variations, or potential reasons for the discrepancies, if applicable.

                    Based on this assement, give it a score between 0 and 10, where 0 indicates that PDFB does not reproduce PDFA's results
                    at all, and 10 indicates that PDFB reproduces PDFA's results perfectly.

                    PDFA: '''{pdfA_path}'''
                    PDFB citations: ''{pdfB_page}''
                    """
                    response = get_completion(prompt)
                    print("Response from OpenAI API:")
                    # print(response)
                    device.close()
                    response = output_string.getvalue()
                    output_string.close()
                    return response


            # print("Citations found:", citations_found, "\n")

    # # Generate the citation tree
    # target_paper = createPaperFromDoi("target_paper_doi")  # Replace "target_paper_doi" with the actual DOI
    # citation_tree = CitationTree(target_paper).retrieveGraph()

    # # Iterate over the nodes in the citation tree
    # for node in citation_tree.nodes:
    #     doi = citation_tree.nodes[node]['data'].doi

    #     # Skip the target paper itself
    #     if doi == target_paper.doi:
    #         continue

    # Analyze the paper or the abstract
    # if indicator == True:
        # # Send prompt to OpenAI API to check if PDF2 reproduces the results of PDF1
        # prompt = f"""

        # Reproducibility is a fundamental aspect of scientific research, ensuring that the results, findings, and methodologies
        # presented in a paper can be independently validated and verified. You need to act like a Research Engineer in the 
        # field of mechanical and aerospace engineering. Part of your role involves assessing the reproducibility of academic
        # papers and assess their effectiveness in addressing specific engineering challenges. 

        # You are given two PDFs, PDFA and PDFB. PDFA is the original paper, which is delimited by triple backticks. PDFB is a
        # paper that cites PDFA. You are given the relevant pages within PDFB that cite and utilize PDFA i.e. PDFB citations,
        # which is delimited by double backticks. Your task is to check if PDFB reproduces the results of PDFA.

        # To analyze the reproducibility of PDFA based on the citations and content in PDFB, follow these directions:
        
        # 1. Examine PDFB citations. Look for indications of whether PDFB attempted to reproduce the results 
        #    of PDFA or if it simply cited PDFA as a reference without attempting reproduction.
        # 2. If PDFB states or implies that it reproduced PDFA's results, carefully scrutinize the corresponding sections or 
        #    code snippets in PDFB. Compare the reported results in PDFA with those in PDFB to verify if they align.
        # 3. Note any discrepancies or differences in the reproduced results between PDFA and PDFB. If PDFB successfully 
        #    reproduces PDFA's results, clearly state that the reproduction was successful. On the other hand, if PDFB produces 
        #    results that directly contradict or deviate significantly from PDFA's results, explicitly mention the discrepancies
        #    and highlight that PDFB's results do not align with PDFA's findings.
        # 4. Provide a detailed analysis of the similarities or differences between PDFA and PDFB, specifically in terms of the
        #    reproduced results. Explain any modifications, variations, or potential reasons for the discrepancies, if applicable.

        # Based on this assement, give it a score between 0 and 10, where 0 indicates that PDFB does not reproduce PDFA's results
        # at all, and 10 indicates that PDFB reproduces PDFA's results perfectly.

        # PDFA: '''{pdfA_path}'''
        # PDFB citations: ''{citations_found}''
        # """
        # response = get_completion(prompt)
        # print("Response from OpenAI API:")
        # # print(response)
        # device.close()
        # response = output_string.getvalue()
        # output_string.close()
        # return response

    # else:
    #     # Use the abstract for prompt engineering
    #     prompt = f"""
    #     Reproducibility is a fundamental aspect of scientific research, ensuring that the results, findings, and methodologies
    #     presented in a paper can be independently validated and verified. As a Research Engineer in the field of mechanical and
    #     aerospace engineering, part of your role is to assess the reproducibility of academic papers and evaluate their effectiveness
    #     in addressing specific engineering challenges.

    #     You are given two papers, PDFA and PDFB. PDFA is the original paper, and PDFB is a paper that cites PDFA. However, the PDFs
    #     are not available for analysis, and only the abstracts are provided. Your task is to assess the reproducibility of PDFA
    #     based on the citations and the abstracts of PDFB. Note that the absence of the full PDF content may limit the accuracy of
    #     the reproducibility analysis.

    #     To analyze the reproducibility of PDFA based on the citations and content in PDFB, follow these directions:

    #     1. Examine the citations in PDFB. Look for indications of whether PDFB attempted to reproduce the results of PDFA or if it
    #     simply cited PDFA as a reference without attempting reproduction.

    #     2. If PDFB states or implies that it reproduced PDFA's results, carefully scrutinize the corresponding sections or code
    #     snippets in PDFB. Compare the reported results in PDFA with those in PDFB to verify if they align.

    #     3. Note any discrepancies or differences in the reproduced results between PDFA and PDFB. If PDFB indicates successful
    #     reproduction of PDFA's results, clearly state that the reproduction was successful. On the other hand, if PDFB produces
    #     results that directly contradict or deviate significantly from PDFA's results, explicitly mention the discrepancies and
    #     highlight that PDFB's results do not align with PDFA's findings.

    #     4. Provide a detailed analysis of the similarities or differences between PDFA and PDFB based on their abstracts. Explain
    #     any modifications, variations, or potential reasons for the discrepancies, considering the limitations of abstract-based
    #     comparison.

    #     Please note that the absence of the full PDF content may limit the accuracy of the reproducibility assessment. 

    #     Abstract of the paper with DOI {abstract}:
    #     {abstract}
    #     """
    #     response = get_completion(prompt)
    #     print("Response from OpenAI API:")
    #     # print(response)
    #     device.close()
    #     response = output_string.getvalue()
    #     output_string.close()
    #     return response


# Paths to the PDF files
# pdfA_path = "/Users/devanshijain/Documents/GitHub/replication_analyzer/pdfA.pdf"
# pdfB_path = "/Users/devanshijain/Documents/GitHub/replication_analyzer/pdfB.pdf"

# Find citations in PDF2 and check if it reproduces the results of PDF1
# check_reproduction(pdfA_path, pdfB_path)


        # Your main goal is to formulate a score to assess the correlation between two papers based on reproduction status and
        # mutual citations. Here is the Scoring Formula:

        #         Score(A, B) = ReproductionScore(A, B) + Σ(0.5 * InitialScore(A, B)) for all mutual citations

        # ReproductionScore(A, B): Assign a positive value (e.g., +1) if Paper A successfully reproduces the results of Paper B.
        # Otherwise, assign a negative value (e.g., -1).

        # InitialScore(A, B): Start with an initial score of zero for each paper pair.

        # Mutual citations: Identify instances where Paper A cites Paper B and vice versa.

        # Propagation factor: Multiply the initial score by 0.5 to account for mutual support.

        # Σ: Summation of the propagation factor multiplied by the initial score for all mutual citations.



        
        # Write the best prompt to and specify how to perfectly score the correlation between two papers. 

if __name__ == "__main__":
    print(check_reproduction(pdfA_path = "pdfA.pdf", pdfB_path = "pdfB.pdf", indicator=True))









