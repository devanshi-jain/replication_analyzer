from paper_repository import Paper
from utils import createPaperFromDoi
import networkx as nx

class CitationNode:
    def __init__(self, paper):
        self.title = paper.title
        self.doi = paper.doi
        self.sources = paper.sources #list of DOIs
        self.cited_by = paper.cited_by #list of DOIs
        self.val = 0
    
    def retrieveCitedBy(self):
        return self.cited_by
    
    def retrieveSources(self):
        return self.sources

    def retrieveVal(self):
        return self.val

class CitationTree:
    def __init__(self, paper):
        self.graph = nx.DiGraph()
        self.generateFromSeed(paper)
    

    #method: generate individual DOI nodes, including their CitationNodes, with directed graph relationships.
        #doi(number/letter) indicates the level of the paper relative to others in terms of degree relationship. 
        #doi2 refers to 2 degrees of seperation in the cited by (upward direction)
        #doi1 refers to 1 degree of seperation (the people who cite the target paper directly)
        #doisub1 refers to 1 degree of seperation, in the reference direction, (what the target paper cites)
        #doi0 refers to the 2 degree seperation, but in a reference then cited by direction, putting it on the same level/recency as the target paper.
    def generateFromSeed(self, paper):

        seed = CitationNode(paper)
        self.graph.add_node(seed.doi, data=seed)

        #expand the seed toward the citeby
        for doi1 in seed.cited_by:
            #first, create a directed entry back toward the seed node.
            layer1paper = createPaperFromDoi(doi1)
            if layer1paper != -1:
                layer1node = CitationNode(layer1paper)
                self.graph.add_node(doi1, data=layer1node)
                self.graph.add_edge(seed.doi, doi1, weight=4)
                #now, create the directed entry from the second degree nodes
                for doi2 in layer1node.cited_by:
                    layer2paper = createPaperFromDoi(doi2)
                    if createPaperFromDoi(doi2) != -1:
                        layer2node = CitationNode(layer2paper)
                        self.graph.add_node(doi2, data=layer2node)
                        self.graph.add_edge(doi1, doi2, weight=4)
            else:
                print("Paper data not found!")
                continue
        
        #now, expand the seed toward the sources
        for doisub1 in seed.sources:
            layersub1paper = createPaperFromDoi(doisub1)
            if layersub1paper != -1:
                layersub1node = CitationNode(layersub1paper)
                self.graph.add_node(doisub1, data=layersub1node)
                self.graph.add_edge(doisub1, seed.doi, weight=4)
                #now, create the directed entry to the middle layer nodes
                for doi0 in layersub1node.sources:
                    layer0paper = createPaperFromDoi(doi0)
                    if createPaperFromDoi(doi0) != -1:
                        layer0node = CitationNode(layer0paper)
                        self.graph.add_node(doi0, data=layer0node)
                        self.graph.add_edge(doisub1, doi0, weight=4)

    #return the graph to process in the main function
    def retrieveGraph(self):
        return self.graph