from paper_repository import Paper
from utils import createPaperLiteFromDoi, createPaperFromDoi, createPaperLessLiteFromDoi
import networkx as nx
import matplotlib.pyplot as plt
import opencitingpy
import mplcursors
import numpy as np
import random
from display import displayInteractableGraph

class CitationNode:
    def __init__(self, paper):
        self.title = paper.title
        self.paper = paper
        self.author = paper.author
        self.doi = paper.doi
        self.val = 0
        self.tier = 0
        self.xtier=0
    
    def retrieveCitedBy(self):
        return self.cited_by
    
    def retrieveSources(self):
        return self.sources

    def retrieveVal(self):
        return self.val

class CitationTree:
    def __init__(self, paper):
        self.graph = nx.DiGraph()
        client = opencitingpy.client.Client()
        self.root = None
        self.generateFromPaper(paper, client)

    #method: generate individual DOI nodes, including their CitationNodes, with directed graph relationships.
        #doi(number/letter) indicates the level of the paper relative to others in terms of degree relationship. 
        #doi2 refers to 2 degrees of seperation in the cited by (upward direction)
        #doi1 refers to 1 degree of seperation (the people who cite the target paper directly)
        #doisub1 refers to 1 degree of seperation, in the reference direction, (what the target paper cites)
        #doi0 refers to the 2 degree seperation, but in a reference then cited by direction, putting it on the same level/recency as the target paper.
    def generateFromPaper(self, paper, client):

        seed = CitationNode(paper)
        self.graph.add_node(seed.doi, data=seed)
        self.root = seed

        #expand the seed toward the citeby
        #now, expand the seed toward the sources
        neglist = []
        cap = 5
        maxlen = min(cap, len(paper.sources)) #creating artificial cap for computation reasons
        xpos=-((cap - 1) / 2)
        for doisub1 in paper.sources[:maxlen]:
            print("Layer -1 Retrieval")
            layersub1paper = createPaperLiteFromDoi(doisub1, client)
            if layersub1paper != -1:
                # print("Layer 0 Retrieval")
                layersub1node = CitationNode(layersub1paper)
                layersub1node.tier = -1
                layersub1node.xtier = xpos
                xpos+=1
                self.graph.add_node(doisub1, data=layersub1node)
                self.graph.add_edge(doisub1, seed.doi, weight=4)
                neglist.append(doisub1)
                #now, create the directed entry to the middle layer nodes
                # for doi0 in layersub1node.sources:
                #     layer0paper = createPaperFromDoi(doi0)
                #     if createPaperFromDoi(doi0) != -1:
                #         layer0node = CitationNode(layer0paper)
                #         self.graph.add_node(doi0, data=layer0node)
                #         self.graph.add_edge(doisub1, doi0, weight=4)

        maxlen = min(cap, len(paper.cited_by)) #creating artificial cap for computation reasons
        xpos = -((cap - 1) / 2)
        for doi1 in paper.cited_by[:maxlen]:
            #first, create a directed entry back toward the seed node.
            print("Layer 1 Retrieval")
            layer1paper = createPaperLessLiteFromDoi(doi1, client)
            if layer1paper != -1:
                # print("Layer 2 Retrieval")
                layer1node = CitationNode(layer1paper)
                layer1node.tier = 1
                layer1node.xtier = xpos
                xpos+=1
                self.graph.add_node(doi1, data=layer1node)
                self.graph.add_edge(seed.doi, doi1, weight=4)

                #special program to link across the first layer
                for doi in layer1paper.sources:
                    if doi in neglist and doi != seed.doi:
                        self.graph.add_edge(doi, doi1, weight=4)
                #now, create the directed entry from the second degree nodes
                # for doi2 in layer1node.cited_by:
                #     layer2paper = createPaperFromDoi(doi2)
                #     if createPaperFromDoi(doi2) != -1:
                #         layer2node = CitationNode(layer2paper)
                #         self.graph.add_node(doi2, data=layer2node)
                #         self.graph.add_edge(doi1, doi2, weight=4)
            else:
                print("Paper data not found!")
                continue

    #return the graph to process in the main function
    def retrieveGraph(self):
        return self.graph
    
if __name__ == "__main__":
    client = opencitingpy.client.Client()
    test = createPaperFromDoi("10.1186/1756-8722-6-59", client)
    tree = CitationTree(test).retrieveGraph()
    print(tree)

    displayInteractableGraph(tree)