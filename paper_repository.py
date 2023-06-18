import opencitingpy

class Paper:
    def __init__(self, title, doi, cited_by=None, sources=None, clusters=[], reproducibility=0,
                 publication_date=None):
        client = opencitingpy.client.Client()
        self.title = title
        self.doi = doi
        print("Retrieving Citations...")
        self.cited_by = client.get_citations(doi)
        print("Retrieving Sources...")
        self.sources = client.get_references(doi)
        self.clusters = clusters
        self.reproducibility = reproducibility
        print("Retrieving Metadata...")
        self.publication_date = client.get_metadata(doi)[1] #retrieve the year

    def add_citation(self, paper):
        self.cited_by.append(paper)

    def add_source(self, paper):
        self.sources.append(paper)

    def add_to_cluster(self, cluster):
        self.clusters.append(cluster)

    def set_reproducibility_cluster(self, cluster):
        self.reproducibility_cluster = cluster


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
