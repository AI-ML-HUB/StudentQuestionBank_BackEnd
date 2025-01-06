# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from firebase_functions import https_fn
from firebase_admin import initialize_app
from firebase_functions.params import SecretParam
from google.cloud import firestore

import flask
from flask import request, jsonify
import json
import os

from google.oauth2 import service_account
from google.auth import default
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta, timezone



SERVICE_ACCOUNT = SecretParam('SERVICE_ACCOUNT')
FOLDER_ID = '1-vdHwarvsDgqTCGZaheZMEz0js4e3sYl'

initialize_app()




app = flask.Flask(__name__)


@app.get("/")
def hello_world() :
    return "Hello World! FLASK"

@app.route('/file-uploaded', methods=['POST'])
def file_uploaded():
    
    #get_drive_service()

    try:
        

        # Get file metadata
        new_files = get_recent_files_in_folder()
        updated_file_data, filtered_new_files = filter_files(new_files)
        for file in filtered_new_files:
            process_file(file)
            #delete_file(file)

        # Save the updated list to Firestore
        save_new_files(get_doc_ref(), updated_file_data)

        return f"All Files processed successfully.", 200

    except Exception as e:
        print(f"Error processing notification: {e}")
        return jsonify({"status": "error", "message": "Failed to process notification."}), 500

def process_file(file):
    print(f"Processing file: {file['name']} (ID: {file['id']})")

def filter_files(new_files):
    # Prepare new file data
    new_file_data = [{"id": file["id"], "name": file["name"]} for file in new_files]

    # Firestore reference
    doc_ref = get_doc_ref()
    
    # Fetch existing data from Firestore
    existing_data = doc_ref.get().to_dict()
    
    if existing_data and "processed_files" in existing_data:
        # Create a set of existing file IDs
        existing_file_ids = {file["id"] for file in existing_data["processed_files"]}

        # Filter out files that already exist
        filtered_new_files = [file for file in new_file_data if file["id"] not in existing_file_ids]

        # Merge the new files into the existing list
        updated_file_data = existing_data["processed_files"] + filtered_new_files
    else:
        # No existing data, use the new data directly
        filtered_new_files = new_file_data
        updated_file_data = filtered_new_files

    return updated_file_data, filtered_new_files

def save_new_files(doc_ref, updated_file_data):
    doc_ref.set({"processed_files": updated_file_data})

def get_doc_ref():    
    # Firestore client
    firestore_client = firestore.Client()
    return firestore_client.collection("questions").document("image_folder")

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
    
def get_recent_files_in_folder():
    """
    Fetch recently uploaded files in a folder.
    :param folder_id: ID of the Google Drive folder.
    :return: List of recently added files.
    """
    try:
        # Load credentials from a service account JSON file
        credentials = get_default_cred()

        # Build the Google Drive API client
        service = build('drive', 'v3', credentials=credentials)

        # Define a time window to identify recent changes (e.g., last 8 hours)
        time_window = datetime.now(timezone.utc) - timedelta(minutes=480)
        time_window_str = time_window.isoformat() 

        # Query for files in the folder modified within the time window
        query = f"'{FOLDER_ID}' in parents and trashed = false and modifiedTime > '{time_window_str}'"
        print(f"google account - {get_service_account_email(credentials)}")
        print(f"Query - '{query}'")
        results = service.files().list(q=query, fields="files(id, name)").execute()

        return results.get('files', [])

    except Exception as error:
        print(f"Error fetching recent files: {error}")
        return []

def get_service_account_email(credentials):

    # Check if credentials have a client_email attribute
    if hasattr(credentials, 'service_account_email'):
        return credentials.service_account_email
    elif hasattr(credentials, 'client_email'):
        return credentials.client_email
    else:
        return "Email not available for these credentials"

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
    
def get_file_name(resource_id):
    """Fetch the file name using the resource ID."""
    try:
        # Authenticate and initialize the Drive API client
        credentials, _ = default()
        service = build('drive', 'v3', credentials=credentials)

        # Retrieve the file metadata
        file_metadata = service.files().get(fileId=resource_id, fields="name").execute()
        return file_metadata.get('name', 'Unknown File')
    except HttpError as error:
        print(f"Failed to fetch file metadata: {error}")
        return 'Unknown File'
    
def download_file(file_name, request_file):
    with open(file_name, 'wb') as file:
        downloader = MediaIoBaseDownload(file, request_file)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download progress: {int(status.progress() * 100)}%")
    
#main url for student question bank back end
@https_fn.on_request(secrets=[SERVICE_ACCOUNT])
def student_qb_be(req: https_fn.Request) -> https_fn.Response:
     with app.request_context(req.environ):
        return app.full_dispatch_request()