import os
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

# Path to the local folder you want to upload
local_folder_path = os.getcwd() + "/downloadedPapers"

# Path to your service account credentials JSON file
credentials_path = "credentials.json"

# ID of the destination folder in Google Drive
drive_folder_id = "1bBapqgfXEaLQbYiaO-iD1rFUg9pN3qLh"

# Authenticate and create a Drive service instance
credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=["https://www.googleapis.com/auth/drive"])
drive_service = build("drive", "v3", credentials=credentials)

# Function to recursively upload files and subfolders to Google Drive
def upload_folder_to_drive(folder_path, parent_folder_id):
    folder_name = os.path.basename(folder_path)

    # # Create the folder in Google Drive
    # folder_metadata = {
    #     "name": folder_name,
    #     "mimeType": "application/vnd.google-apps.folder",
    #     "parents": [parent_folder_id]
    # }
    # folder = drive_service.files().create(body=folder_metadata, fields="id").execute()
    # folder_id = folder.get("id")

    # Upload files in the folder
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            media = MediaFileUpload(file_path)
            file_metadata = {
                "name": file_name,
                "parents": [parent_folder_id]
            }
            drive_service.files().create(body=file_metadata, media_body=media).execute()
        elif os.path.isdir(file_path):
            upload_folder_to_drive(file_path, parent_folder_id)

    print(f"Uploaded folder '{folder_name}' to Google Drive with ID: {parent_folder_id}")

# Start uploading the local folder
upload_folder_to_drive(local_folder_path, drive_folder_id)
