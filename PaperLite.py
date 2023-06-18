class PaperLite:
    def __init__(self, title, doi, cited_by=None, sources=None, clusters=[], reproducibility=0,
                 publication_date=None, author = None):
        client = opencitingpy.client.Client()
        self.title = title
        self.doi = doi

        self.clusters = clusters
        self.reproducibility = reproducibility
        print("Init Success!")

    def add_to_cluster(self, cluster):
        self.clusters.append(cluster)

    def set_reproducibility_cluster(self, cluster):
        self.reproducibility_cluster = cluster

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)

