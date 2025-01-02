# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from firebase_functions import https_fn
from firebase_admin import initialize_app
from firebase_functions.params import SecretParam

import flask
from flask import request
import json

from google.oauth2 import service_account
from google.auth import default
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload



initialize_app()

# Set up Google Drive API

SERVICE_ACCOUNT = SecretParam('SERVICE_ACCOUNT')
SCOPES = ['https://www.googleapis.com/auth/drive']

credentials = service_account.Credentials.from_service_account_info(
    json.loads(SERVICE_ACCOUNT.value),
    scopes=SCOPES
)

drive_service = build('drive', 'v3', credentials=credentials)


app = flask.Flask(__name__)


@app.get("/")
def hello_world() :
    return "Hello World! FLASK"

@app.route('/file-uploaded', methods=['POST'])
def file_uploaded():
    # Parse the request body
    notification_data = request.json
    print(f"Notification received: {notification_data}")

    # Get file ID from the notification
    file_id = notification_data.get('fileId')

    if file_id:
        # Get file metadata
        file_metadata = drive_service.files().get(fileId=file_id).execute()
        file_name = file_metadata.get('name')
        print(f"File uploaded: {file_name}")

        # Optional: Download the file
        #request_file = drive_service.files().get_media(fileId=file_id)
        #download_file(file_name, request_file)

        return f"File {file_name} processed successfully.", 200
    else:
        return "File ID not found in notification.", 400

def download_file(file_name, request_file):
    with open(file_name, 'wb') as file:
        downloader = MediaIoBaseDownload(file, request_file)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download progress: {int(status.progress() * 100)}%")
    
#main url for student question bank back end
@https_fn.on_request()
def student_qb_be(req: https_fn.Request) -> https_fn.Response:
     with app.request_context(req.environ):
        return app.full_dispatch_request()