import opencitingpy
import json

class Paper:
    def __init__(self, title, doi, cited_by=None, sources=None, publication_date=None, author = None, client = None, num_citations = None):
        if client == None:
            client = opencitingpy.client.Client()
        self.title = title
        self.doi = doi
        #print("Retrieving Citations...")
        if cited_by == None:
            self.cited_by = [x.citing[8:] for x in client.get_citations(doi)]
        else:
            self.cited_by = cited_by
        #print("Retrieving Sources...")
        if sources == None:
            self.sources = [x.cited[8:] for x in client.get_references(doi)]
        else:
            self.sources = sources
        self.metadata = client.get_metadata(doi)
        if self.metadata != []:
            self.author = self.metadata[0].author
            self.publication_date = self.metadata[0].year
            self.num_citations = self.metadata[0].citation_count

    def add_citation(self, paper):
        self.cited_by.append(paper)

    def add_source(self, paper):
        self.sources.append(paper)

    def add_to_cluster(self, cluster):
        self.clusters.append(cluster)

    def set_reproducibility_cluster(self, cluster):
        self.reproducibility_cluster = cluster

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)

class PaperLite:
    def __init__(self, title, doi,  publication_date=None, author = None, client = None):
        if client == None:
            client = opencitingpy.client.Client()
        self.metadata = client.get_metadata(doi)
        if self.metadata != []:
            self.author = self.metadata[0].author
        self.title = title
        self.doi = doi

    def add_to_cluster(self, cluster):
        self.clusters.append(cluster)

    def set_reproducibility_cluster(self, cluster):
        self.reproducibility_cluster = cluster

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)
    
class PaperLessLite:
    def __init__(self, title, doi, sources=None, reproducibility=0,
                 publication_date=None, author = None, client = None):
        if client == None:
            client = opencitingpy.client.Client()
        client = opencitingpy.client.Client()
        self.title = title
        self.doi = doi
        if sources == None:
            self.sources = [x.cited[8:] for x in client.get_references(doi)]
        else:
            self.sources = sources
        self.metadata = client.get_metadata(doi)
        if self.metadata != []:
            self.author = self.metadata[0].author

    def add_citation(self, paper):
        self.cited_by.append(paper)

    def add_source(self, paper):
        self.sources.append(paper)

    def add_to_cluster(self, cluster):
        self.clusters.append(cluster)

    def set_reproducibility_cluster(self, cluster):
        self.reproducibility_cluster = cluster

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)

# class ResearchPaperRepository:
#     def __init__(self):
#         self.papers = []

#     def add_paper(self, paper):
#         self.papers.append(paper)

#     def get_paper_by_title(self, title):
#         for paper in self.papers:
#             if paper.title == title:
#                 return paper
#         return None

#     def get_papers_by_author(self, author_name):
#         return [paper for paper in self.papers if author_name in paper.authors]

#     def get_papers_citing_paper(self, paper_title):
#         return [paper for paper in self.papers if paper_title in [cited_paper.title for cited_paper in paper.cited_by]]

#     def get_papers_cited_by_paper(self, paper_title):
#         return [paper for paper in self.papers if paper_title in [source_paper.title for source_paper in paper.sources]]

#     def get_papers_in_reproducibility_cluster(self, cluster):
#         return [paper for paper in self.papers if paper.reproducibility_cluster == cluster]

#     def traverse_papers_backwards(self, paper, visit_func):
#         visit_func(paper)
#         if paper.publication_date is not None:
#             for source_paper in paper.sources:
#                 if source_paper.publication_date is not None and source_paper.publication_date < paper.publication_date:
#                     self.traverse_papers_backwards(source_paper, visit_func)
