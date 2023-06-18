import opencitingpy
from paper_repository import Paper, PaperLite

def createPaperFromDoi(doi):
    client = opencitingpy.client.Client()
    metadata = client.get_metadata(doi)
    cited_by = [x.citing[8:] for x in client.get_citations(doi)]
    sources = [x.cited[8:] for x in client.get_references(doi)]
    if metadata == []:
        return -1
    metadata = metadata[0]
    return Paper(title = metadata.title, doi = doi, cited_by = cited_by, sources = sources, publication_date = metadata.year)

def createPaperLiteFromDoi(doi):
    client = opencitingpy.client.Client()
    metadata = client.get_metadata(doi)
    if metadata == []:
        return -1
    metadata = metadata[0]
    return PaperLite(title = metadata.title, doi = doi, publication_date = metadata.year)

#outputs a return code: 0 if retrieved successfully, -1 if not retrieved (will be used to determine whether or not to use abstract)
def retrievePaperFromDrive(title):
    return -1