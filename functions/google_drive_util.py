from datetime import datetime, timedelta, timezone
import json
import os
from io import BytesIO

from firebase_functions.params import SecretParam

from google.auth import default
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload




SERVICE_ACCOUNT = SecretParam('SERVICE_ACCOUNT')
FOLDER_ID = '1-vdHwarvsDgqTCGZaheZMEz0js4e3sYl'


def get_cred():
    scopes = ['https://www.googleapis.com/auth/drive']

    credentials = service_account.Credentials.from_service_account_info(
        json.loads(SERVICE_ACCOUNT.value),
        scopes=scopes
    )

    return credentials


def get_default_cred():
    credentials, _ = default()
    return credentials


def delete_file(file):
    """
    delete file from drive
    """

    try:
       # Load credentials from a service account JSON file
        credentials = get_default_cred()

        # Build the Google Drive API client
        drive_service = build('drive', 'v3', credentials=credentials)

        # Delete the file using Google Drive API
        drive_service.files().delete(fileId=file['id']).execute()

        print(f"Deleted file: {file['name']} (ID: {file['id']})")
    except Exception as error:
        print(f"Error deleting file: {error}")



def get_service_account_email(credentials):

    # Check if credentials have a client_email attribute
    if hasattr(credentials, 'service_account_email'):
        return credentials.service_account_email
    elif hasattr(credentials, 'client_email'):
        return credentials.client_email
    else:
        return "Email not available for these credentials"


def get_recent_files_in_folder():
    """
    Fetch recently uploaded files in a folder.
    :param folder_id: ID of the Google Drive folder.
    :return: List of recently added files.
    """
    try:
        service = get_service()

        # Define a time window to identify recent changes (e.g., last 8 hours)
        time_window = datetime.now(timezone.utc) - timedelta(minutes=480)
        time_window_str = time_window.isoformat()

        # Query for files in the folder modified within the time window
        query = f"'{FOLDER_ID}' in parents and trashed = false and modifiedTime > '{time_window_str}'"
        print(f"Query - '{query}'")
        results = service.files().list(q=query, fields="files(id, name)").execute()

        return results.get('files', [])

    except Exception as error:
        print(f"Error fetching recent files: {error}")
        return []

def get_service():
    # Load credentials from a service account JSON file
    credentials = get_default_cred()

    # Build the Google Drive API client
    service = build('drive', 'v3', credentials=credentials)
    print(f"google account - {get_service_account_email(credentials)}")
    return service


def download_file(file):
    print(f"Downloading file: {file['name']} (ID: {file['id']})")
    file_name = file['name']
    file_id = file['id']

    service = get_service()
    request_file = service.files().get_media(fileId=file_id)
    
    
    # Create a BytesIO buffer to store the file content
    buffer = BytesIO()
    
    
        
    downloader = MediaIoBaseDownload(buffer, request_file)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"Download progress: {int(status.progress() * 100)}%")
    
    # Get the content as bytes
    buffer.seek(0)  # Reset the buffer's position
    file_bytes = buffer.read()

    return file_bytes