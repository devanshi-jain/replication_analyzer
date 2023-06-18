
import pandas as pd
from scidownl import scihub_download

data= pd.read_csv("Stone, Howard A.csv")
no_of_rows = data.shape[0]

from paper_repository import Paper

for i in range(0, no_of_rows): 

    try:
        DOI = data.iloc[i, 12]
        TITLE = data.iloc[i, 2]
        paper = "https://doi.org/" + DOI
        
        out = "/Users/manan/Desktop/calhacks/PDFs/" + TITLE
        paper_type = "doi"

        proxies = {
            'http': 'socks5://127.0.0.1:7890'
        }
        scihub_download(paper, paper_type=paper_type, out=out, proxies=proxies)
        dl_paper = Paper(title = TITLE, doi = DOI)
        
         

    except:
        continue
