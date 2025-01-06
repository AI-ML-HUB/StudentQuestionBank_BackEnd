# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from firebase_functions import https_fn
from firebase_admin import initialize_app

import flask
from flask import request, jsonify
import os

from google.auth import default

from firestore_util import get_doc_ref, get_processed_files
from ai_tasks import getText
from firestore_util import filter_files, save_new_files
from ai_tasks import process_file
from google_drive_util import SERVICE_ACCOUNT, get_recent_files_in_folder, download_file



initialize_app()




app = flask.Flask(__name__)


@app.get("/")
def hello_world() :
    return getText()

@app.get("/prcessed_files")
def prcessed_files() :
    # Fetch existing data from Firestore
    existing_data = get_processed_files()
    
    return jsonify(existing_data)

@app.route('/file-uploaded', methods=['POST'])
def file_uploaded():
    
    #get_drive_service()

    try:
        

        # Get file metadata
        new_files = get_recent_files_in_folder()
        updated_file_data, filtered_new_files = filter_files(new_files)
        for file in filtered_new_files:
            download_file(file)
            process_file(file)
            #delete_file(file)

        # Save the updated list to Firestore
        save_new_files(get_doc_ref(), updated_file_data)

        return f"All Files processed successfully.", 200

    except Exception as e:
        print(f"Error processing notification: {e}")
        return jsonify({"status": "error", "message": "Failed to process notification."}), 500

#main url for student question bank back end
@https_fn.on_request(secrets=[SERVICE_ACCOUNT])
def student_qb_be(req: https_fn.Request) -> https_fn.Response:
     with app.request_context(req.environ):
        return app.full_dispatch_request()