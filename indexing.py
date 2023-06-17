from dotenv import load_dotenv
import os
import logging
import sys
import requests
import requests
# from pybtex.database import parse_file

# bibtex_file = "bibtex.bib"

# # Parse the bibtex file
# bib_data = parse_file(bibtex_file)

# # Extract the first entry from the bibtex file
# entry = list(bib_data.entries.values())[0]

# # Extract the PDF URL from the bibtex entry
# pdf_url = entry.fields["url"]

# # Send a GET request to download the PDF file
# response = requests.get(pdf_url)

# # Save the PDF file in the current directory
# with open("paper.pdf", "wb") as file:
#     file.write(response.content)


# logging.basicConfig(stream=sys.stdout, level=logging.INFO)
# logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

# from llama_index import GPTVectorStoreIndex, download_loader
# from IPython.display import Markdown, display

# # Reference: https://colab.research.google.com/drive/12cdBWMpOfCxpiAS1zSqZRY66o84qMiTo?usp=sharing#scrollTo=690a6918-7c75-4f95-9ccc-d2c4a1fe00d7

# # To use SimpleWebPageReader

# # build index # download web page loader from LlamaHub
# SimpleWebPageReader = download_loader("SimpleWebPageReader")

# # load in PG's essay
# documents = SimpleWebPageReader(html_to_text=True).load_data(["http://paulgraham.com/worked.html"])

# documents[0].get_text()

# index = GPTVectorStoreIndex.from_documents(documents)
# # load_dotenv()
# # set Logging to DEBUG for more detailed outputs
# query_engine = index.as_query_engine()
# response = query_engine.query("What did the author do growing up?")
# display(Markdown(f"<b>{response}</b>"))

# sn1 = response.source_nodes[0]
# sn1.similarity
# print(sn1.node.get_text())

# # set Logging to DEBUG for more detailed outputs
# query_engine = index.as_query_engine()
# response = query_engine.query("What are times the author was angry?")

# # display(Markdown(f"<b>{response}</b>"))
# # print(response.get_formatted_sources())

# # # Use Image Reader

# # from llama_index.response.notebook_utils import (
# #     display_response,
# #     display_image,
# # )
# # from llama_index.indices.query.query_transform.base import (
# #     ImageOutputQueryTransform,
# # )

# import PyPDF2

# def extract_text_from_pdf(file_path):
#     with open(file_path, 'rb') as file:
#         reader = PyPDF2.PdfFileReader(file)
#         text = ""
#         for page_num in range(reader.numPages):
#             page = reader.getPage(page_num)
#             text += page.extractText()
#         return text

# def find_citations(text):
#     # Perform citation extraction logic here
#     # You can use regular expressions or other techniques to identify citations
    
#     # Example: Identifying citations in square brackets, e.g., [1], [2], etc.
#     import re
#     citations = re.findall(r'\[\d+\]', text)
#     return citations

# def check_citation(citations, target_paper_title):
#     for citation in citations:
#         if target_paper_title in citation:
#             return True
#     return False

# # PDF file paths
# pdf1_path = 'path/to/first_paper.pdf'
# pdf2_path = 'path/to/second_paper.pdf'

# # Extract text from PDFs
# pdf1_text = extract_text_from_pdf(pdf1_path)
# pdf2_text = extract_text_from_pdf(pdf2_path)

# # Find citations in each paper
# pdf1_citations = find_citations(pdf1_text)
# pdf2_citations = find_citations(pdf2_text)

# # Print the citations
# print("Citations in PDF 1:")
# for citation in pdf1_citations:
#     print(citation)
# print()

# print("Citations in PDF 2:")
# for citation in pdf2_citations:
#     print(citation)
# print()

# # Check if PDF 2 cites PDF 1
# if check_citation(pdf2_citations, "PDF 1 Title"):
#     print("PDF 2 cites PDF 1")
# else:
#     print("PDF 2 does not cite PDF 1")
