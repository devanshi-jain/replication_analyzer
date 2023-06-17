# /////////////////////////////////SETUP////////////////////////////////////////
from dotenv import load_dotenv
import os
import logging
import sys
import requests
import openai
import re

# import necessary libraries
from io import StringIO
from pdfminer.layout import LAParams
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LTTextBox, LTTextLine
from pdfminer.converter import PDFPageAggregator, TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager

load_dotenv()

# Get value of OPENAI_API_KEY environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")

# Set the API key for the OpenAI API client
openai.api_key = openai_api_key


# Function to parse the PDF and extract citations
def parse_pdf_citations(file_path):
    citations = []

    with open(file_path, 'rb') as pdf_file:
        parser = PDFParser(pdf_file)
        document = PDFDocument(parser)
        parser.set_document(document)

        for page in PDFPage.create_pages(document):
            interpreter = PDFPageInterpreter(PDFResourceManager(), PDFPageAggregator(PDFResourceManager()))
            citations_found = False  # Flag to indicate if citations are found on the page
            citations_on_page = []  # List to store citations found on the page

            interpreter.process_page(page)
            layout = interpreter.get_result()

            for element in layout:
                if isinstance(element, LTTextBox) or isinstance(element, LTTextLine):
                    text = element.get_text().strip()

                    # Regular expression pattern to match citations
                    citation_pattern = r"\[(\d+)\]"

                    # Find all citations in the text
                    matches = re.findall(citation_pattern, text)
                    if matches:
                        citations_found = True
                        citations_on_page.extend([int(match) for match in matches])

            if citations_found:
                citations.extend(citations_on_page)

    return citations


pdf_file_path_1 = "/path/to/paper1.pdf"
pdf_file_path_2 = "/path/to/paper2.pdf"

# Create Paper instances for the two papers
paper1 = Paper(title="Paper 1", doi="doi-1", publication_date="2023-06-01")
paper2 = Paper(title="Paper 2", doi="doi-2", publication_date="2023-06-02")

# Extract the citations for paper 1
citations_1 = parse_pdf_citations(pdf_file_path_1)

# Extract the citations for paper 2
citations_2 = parse_pdf_citations(pdf_file_path_2)

# Establish citation relationship between the papers
if paper1.doi in citations_2:
    paper2.add_citation(paper1)

if paper2.doi in citations_1:
    paper1.add_citation(paper2)
