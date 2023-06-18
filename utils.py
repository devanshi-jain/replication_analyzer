import opencitingpy
import os
from paper_repository import Paper, PaperLite, PaperLessLite
from scidownl import scihub_download
import requests
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google.oauth2 import service_account
import io
import random

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
#if the paper is retrieved correctly, will be found at distinct place in cwd.
def retrievePaper(doi):
    proxies = {
        'http': 'socks5://127.0.0.1:7890'
    }
    output = os.getcwd() + "/pdfB.pdf"
    scihub_download("https://doi.org/" + doi, paper_type="doi", out = output, proxies=proxies)
    if os.path.exists(output):
        return 0
    else:
        return -1

#returns the abstract based on a doi
def retrieveAbstract(doi):
    # Construct the API URL with the DOI
    api_url = f"https://api.crossref.org/works/{doi}"
    api_key = "18f11beb55c4b642c2ddf677501ad0c8b909"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'CR-Clickthrough-Client-Token': api_key
        }

        # Send GET request to the API
        response = requests.get(api_url, headers = headers)
        response.raise_for_status()

        # Extract the abstract from the response
        data = response.json()
        abstract = data['message']['abstract']

        return abstract

    except requests.exceptions.RequestException as e:
        print(f"Error retrieving abstract: {str(e)}")
        return -1


#retrieves the paper from drive... should work, no...since we're iterating from the drive lol? If it doesn't, returns -1 to throw an error.
def retrievePaperFromDrive(title):
    #setup to locate the correct file, inverse process as below
    drive_folder_id = "1bBapqgfXEaLQbYiaO-iD1rFUg9pN3qLh"
    credentials_path = "credentials.json"
    pdfName = title + ".pdf"

    credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=["https://www.googleapis.com/auth/drive"])
    drive_service = build("drive", "v3", credentials=credentials)

    try:
        # Search for the PDF file in the folder
        results = drive_service.files().list(
            q=f"'{drive_folder_id}' in parents and name='{pdfName}' and mimeType='application/pdf'",
            fields='files(id)'
        ).execute()

        files = results.get('files', [])

        if len(files) == 0:
            print('PDF not found in the specified folder.')
            return -1

        # Get the ID of the PDF file
        pdf_id = files[0]['id']

        # Prepare the output file stream
        output_file = "pdfA.pdf"
        with io.FileIO(output_file, 'wb') as file:
            # Download the PDF file
            request = drive_service.files().get_media(fileId=pdf_id)
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"Download {int(status.progress() * 100)}%")

        print(f"PDF downloaded successfully as '{output_file}'.")

    except Exception as e:
        print(f"An error occurred while downloading the PDF: {str(e)}")
        return -1

    return 0

def uploadFolderToDrive():
    # Path to the local folder you want to upload
    local_folder_path = os.getcwd() + "/downloadedPapers"

    # Path to your service account credentials JSON file
    credentials_path = "credentials.json"

    # ID of the destination folder in Google Drive
    drive_folder_id = "1bBapqgfXEaLQbYiaO-iD1rFUg9pN3qLh"

    credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=["https://www.googleapis.com/auth/drive"])
    drive_service = build("drive", "v3", credentials=credentials)

    folder_name = os.path.basename(local_folder_path)

    # # Create the folder in Google Drive
    # folder_metadata = {
    #     "name": folder_name,
    #     "mimeType": "application/vnd.google-apps.folder",
    #     "parents": [parent_folder_id]
    # }
    # folder = drive_service.files().create(body=folder_metadata, fields="id").execute()
    # folder_id = folder.get("id")

    # Upload files in the folder, non-recursive implementation
    for file_name in os.listdir(local_folder_path):
        file_path = os.path.join(local_folder_path, file_name)
        if os.path.isfile(file_path):
            media = MediaFileUpload(file_path)
            file_metadata = {
                "name": file_name,
                "parents": [drive_folder_id]
            }
            drive_service.files().create(body=file_metadata, media_body=media).execute()

    print(f"Uploaded folder '{folder_name}' to Google Drive with ID: {drive_folder_id}")

def randomGPTOutput():
    corr, score = random.random(0, 1), random.random(-1, 1)
    return corr, score

if __name__ == "__main__":
    #test case for retrieveAbstract
    doi = "10.1186/1756-8722-6-59"
    abstract = retrieveAbstract(doi)

    if abstract:
        print(f"Abstract: {abstract}")
    else:
        print("Abstract not found.")

    #test case for retrieveFromDrive
    name = "Non-grey gas radiative transfer analyses using the statistical narrow-band modelt"
    retrievePaperFromDrive(name)

    #test case for retrievePaper
    paper = retrievePaper(doi)
    print(paper)