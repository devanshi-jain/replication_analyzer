import opencitingpy
from paper_repository import Paper

def createPaperFromDoi(doi):
    client = opencitingpy.client.Client()
    metadata = client.get_metadata(doi)
    cited_by = [x.citing[8:] for x in client.get_citations(doi)]
    sources = [x.cited[8:] for x in client.get_references(doi)]
    if metadata == []:
        return -1
    metadata = metadata[0]
    return Paper(title = metadata.title, doi = doi, cited_by = cited_by, sources = sources, publication_date = metadata.year)