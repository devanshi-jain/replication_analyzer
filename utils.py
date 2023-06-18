import opencitingpy
from paper_repository import Paper, PaperLite, PaperLessLite

def createPaperFromDoi(doi, client):
    metadata = client.get_metadata(doi)
    cited_by = [x.citing[8:] for x in client.get_citations(doi)]
    sources = [x.cited[8:] for x in client.get_references(doi)]
    if metadata == []:
        return -1
    metadata = metadata[0]
    return Paper(title = metadata.title, doi = doi, cited_by = cited_by, sources = sources, publication_date = metadata.year, author=metadata.author, client = client)

def createPaperLiteFromDoi(doi, client):
    metadata = client.get_metadata(doi)
    if metadata == []:
        return -1
    metadata = metadata[0]
    return PaperLite(title = metadata.title, doi = doi, publication_date = metadata.year)

def createPaperLessLiteFromDoi(doi, client):
    metadata = client.get_metadata(doi)
    if metadata == []:
        return -1
    metadata = metadata[0]
    sources = [x.cited[8:] for x in client.get_references(doi)]
    return PaperLessLite(title = metadata.title, doi = doi, publication_date = metadata.year, client = client, sources = sources)

#outputs a return code: 0 if retrieved successfully, -1 if not retrieved (will be used to determine whether or not to use abstract)
def retrievePaper(title):
    return -1