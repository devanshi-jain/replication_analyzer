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

# function uses the OpenAI API client to generate text based on a prompt using 
def get_completion(prompt, model="gpt-3.5-turbo"):
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
    # Extract the citations from PDF1
    citations_pdfA = parse_pdf_citations(pdfA_path)

    # Extract the content of PDF2 for citation analysis
    with open(pdfB_path, 'rb') as pdfB_file:
        parser = PDFParser(pdfB_file)
        document = PDFDocument(parser)
        parser.set_document(document)

        rsrcmgr = PDFResourceManager()
        device = PDFPageAggregator(rsrcmgr, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        citations_found = []
        for page in PDFPage.create_pages(document):
            interpreter.process_page(page)
            layout = device.get_result()
            for element in layout:
                if isinstance(element, LTTextBox) or isinstance(element, LTTextLine):
                    text = element.get_text().strip()

                    # Check if the text contains any citations from PDF1
                    for citation in citations_pdfA:
                        if f"[{citation}]" in text: #TODO : replace text with page
                            citations_found.append((citation, text))

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
    if indicator == 1:
        # Send prompt to OpenAI API to check if PDF2 reproduces the results of PDF1
        prompt = f"""
        The paper in PDF2 cites the paper in PDF1. Based on this information, does the paper in PDF2 reproduce the results of the paper in PDF1?
        (based on this block of text)
        Write the best prompt to and specify how to perfectly score the correlation between two papers.
        PDF1 citations: {citations_pdfA}
        PDF2 citations: {citations_found}
        """
        response = get_completion(prompt)
        print("Response from OpenAI API:")
        print(response)

    else:
        # Use the abstract for prompt engineering
        prompt = f"""
        Abstract of the paper with DOI {doi}:
        {abstract}
        """
        response = get_completion(prompt)
        print("Response from OpenAI API:")
        print(response)

        
    # # Process the response and give it a score

    # # Add the score to the CitationNode's value
    # # citation_tree.nodes[node]['data'].val = score
    # # Iterate over the nodes in the citation tree
    # for node in citation_tree.nodes:
    #     doi = citation_tree.nodes[node]['data'].doi

    #     # Skip the target paper itself
    #     if doi == target_paper.doi:
    #         continue

    #     # Download or retrieve the paper based on DOI
    #     paper = createPaperFromDoi(doi)

    #     # Calculate the score for the paper
    #     score = calculate_correlation_score(paper)

    #     # Add the score to the CitationNode's value
    #     citation_tree.nodes[node]['data'].val = score


        # propagation formula of scores
        # def calculate_correlation_score(citing_paper):
            # for every two papers, calculate the correlation score
            # reproduced paper gets positive score, non-reproduced paper gets negative score
            # propagate: mutual citations get  -> 0.5 * score
            return 0
            # Generate the multicolored graph based on validation scores
            # Use the citation_tree to plot the graph


# Paths to the PDF files
pdfA_path = "/Users/devanshijain/Documents/GitHub/replication_analyzer/pdfA.pdf"
pdfB_path = "/Users/devanshijain/Documents/GitHub/replication_analyzer/pdfB.pdf"

# Find citations in PDF2 and check if it reproduces the results of PDF1
check_reproduction(pdfA_path, pdfB_path)
