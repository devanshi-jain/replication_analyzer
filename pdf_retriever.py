import json
import pandas as pd
from scidownl import scihub_download
from paper_repository import Paper
import os

data= pd.read_csv("Ju, Yiguang.csv")
no_of_rows = data.shape[0]

file_path = "paperdata.json"
for i in range(0, no_of_rows): 

    try:
        doi = data.iloc[i, 12]
        title = data.iloc[i, 2]
        paper = "https://doi.org/" + doi
        out = os.getcwd() + "/downloadedPapers" + doi
        paper_type = "doi"
        proxies = {
            'http': 'socks5://127.0.0.1:7890'
        }
        scihub_download(paper, paper_type=paper_type, out=out, proxies=proxies)
        dl_paper = Paper(title = title, doi = doi)
        with open(file_path, "a") as file:
            file.write(json.dumps(dl_paper) + ",")

    except:
        continue
