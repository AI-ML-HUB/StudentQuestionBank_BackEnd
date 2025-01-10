# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from firebase_functions import https_fn
from firebase_admin import initialize_app

import flask
from flask import request, jsonify
import os

from google.auth import default

from firestore_util import get_doc_ref, get_phy_questions, get_processed_files, filter_files, save_new_files, save_new_questions
from ai_tasks import getText, process_file, OPENAI_API_KEY
from google_drive_util import SERVICE_ACCOUNT, get_recent_files_in_folder, download_file



initialize_app()




app = flask.Flask(__name__)


@app.get("/")
def hello_world() :
    return getText()

@app.get("/phy_questions")
def get_phyq():
    return jsonify(get_phy_questions())

@app.get("/prcessed_files")
def prcessed_files() :
    # Fetch existing data from Firestore
    existing_data = get_processed_files()
    
    return jsonify(existing_data)

@app.route('/file-uploaded', methods=['POST'])
def file_uploaded():
    

    try:
        # Get file metadata
        new_files = get_recent_files_in_folder()
        updated_file_data, filtered_new_files = filter_files(new_files)
        for file in filtered_new_files:
            file_bytes = download_file(file)
            questions = process_file(file, file_bytes)
            save_new_questions(questions, file['id'])

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