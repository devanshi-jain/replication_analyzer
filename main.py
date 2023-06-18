from utils import retrievePaperFromDrive, retrievePaper, retrieveAbstract
import os
import json
import opencitingpy
from paper_repository import Paper
from citationTree import CitationTree, CitationNode
from promptAgent import check_reproduction

def __main__():
    
    #first, set the PI of interest.
    targetPI_name = "Ju, Yiguang"
    print("Currently examining all papers associated with " + targetPI_name)

    #look through the CSV, download all the papers associated with his, then upload them to drive for storage efficiency.
    #we've already downloaded his papers, so skipping this step.

    #now, look through the generated paperdata.json to determine pull order.
    with open(os.getcwd() + "/paperdata.json", 'r') as json_file:
        for line in json_file:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            
            #loading paper properties
            title = obj["title"]
            doi = obj["doi"]
            cited_by = obj["cited_by"]
            sources = obj["sources"]
            #create the Paper object
            targetPaper = Paper(title = title, doi = doi, cited_by = cited_by, sources = sources)

            #download the target paper.
            if retrievePaperFromDrive(targetPaper.title) == -1:
                print("Error when retrieving paper from drive!")
                continue

            #now, generate the reproducibility tree
            #this might take a while...
            tree = CitationTree(targetPaper)

            #now, we traverse the tree, and perform the reproducibility analysis with ChatGPT
            #first, we obtain the tree elements we want to compare.

            seed = tree.root
            for doi in seed.retrieveCitedBy():
                #first, try to retrieve the paper itself.
                if retrievePaper(doi) == -1:
                    print("Unable to find open-source version of this paper, attempting to retrieve abstract.")
                    abstract = retrieveAbstract(doi)
                    if abstract == -1:
                        print("Unable to locate abstract of this paper. Skipping this node.")
                    else:
                        continue

                else:
                    #do stuff here to check reproduction and propogate the score through associated areas
                    print("Analyzing...")
                    scoreComputer()
                    

            for doi in seed.retrieveSources():
                #first, try to retrieve the paper itself.
                if retrievePaper(doi) == -1:
                    print("Unable to find open-source version of this paper, attempting to retrieve abstract.")
                    abstract = retrieveAbstract(doi)
                    if abstract == -1:
                        print("Unable to locate abstract of this paper. Skipping this node.")
                    else:
                        continue
                else:
                    #do stuff here to check reproduction and propogate the score through associated areas
                    print("Analyzing...")

            #now, present the completed CitationTree, with nodes.
            #dump the tree too as well into a json file

    return 0

def scoreComputer(corr, repScore, DOI1, DOI2):
    #send whatever input is required to the prompt engineer
    #Returns : correlation score[0,1] and reproducibility score [-1,1]
    corr, repScore = 0, 0
    score = corr * repScore
    
    tree.graph.nodes[DOI1][0].val += score
    tree.graph.nodes[DOI2][0].val += score / 2
    
    # Add the score to the CitationNode's value
    # citation_tree.nodes[node]['data'].val = score
    # Iterate over the nodes in the citation tree
    for node in tree.graph.nodes:
        doi = tree.graph.nodes[node]['data'].doi

        # Skip the target paper itself
        if doi == DOI1 or doi == DOI2:
            continue

        # Add the score to the CitationNode's value
        tree.nodes[node]['data'].val = score

