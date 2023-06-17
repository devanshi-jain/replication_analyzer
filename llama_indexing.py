from dotenv import load_dotenv
import os
import logging
import sys
import requests
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
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

