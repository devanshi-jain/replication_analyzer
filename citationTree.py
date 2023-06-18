from paper_repository import Paper
import opencitingpy

class CitationNode:
    def __init__(self, paper):
        self.title = paper.title
        self.sources = paper.sources
        self.cited_by = paper.cited_by
    
    def retrieveCitedBy(self):
        return self.cited_by
    
    def retrieveSources(self):
        return self.sources