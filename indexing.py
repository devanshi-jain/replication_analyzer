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

def check_reproduction(pdf1_path, pdf2_path):
    # Extract the citations from PDF1
    citations_pdf1 = parse_pdf_citations(pdf1_path)

    # Extract the content of PDF2 for citation analysis
    with open(pdf2_path, 'rb') as pdf2_file:
        parser = PDFParser(pdf2_file)
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
                    for citation in citations_pdf1:
                        if f"[{citation}]" in text:
                            citations_found.append((citation, text))

    # Check if PDF2 cites PDF1
    if citations_found:
        print("Citations found in PDF2:")
        for citation, text in citations_found:
            print(f"Citation {citation}: {text}")
    else:
        print("PDF2 does not cite PDF1")

    # Send prompt to OpenAI API to check if PDF2 reproduces the results of PDF1
    prompt = f"""
    The paper in PDF2 cites the paper in PDF1. Based on this information, does the paper in PDF2 reproduce the results of the paper in PDF1?
    (based on this block of text)
    PDF1 citations: {citations_pdf1}
    PDF2 citations: {citations_found}
    """
    response = get_completion(prompt)
    print("Response from OpenAI API:")
    print(response)

# Paths to the PDF files
pdf1_path = "/Users/devanshijain/Documents/GitHub/replication_analyzer/doi_research_papers/Coordinated Speed Oscillations in Schooling Killifish Enrich Social Communication. Journal of Nonlinear Science, 25(5).pdf"
pdf2_path = "/Users/devanshijain/Documents/GitHub/replication_analyzer/doi_research_papers/Decision versus compromise for animal groups in motion. Proceedings of the National Academy of Sciences, 109(1).pdf"

# Find citations in PDF2 and check if it reproduces the results of PDF1
check_reproduction(pdf1_path, pdf2_path)
