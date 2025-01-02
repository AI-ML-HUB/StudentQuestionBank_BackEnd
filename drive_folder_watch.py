import os
from flask import Flask, request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Set up Google Drive API
SERVICE_ACCOUNT_FILE = 'service_account.json'
SCOPES = ['https://www.googleapis.com/auth/drive']
FOLDER_ID = '1-vdHwarvsDgqTCGZaheZMEz0js4e3sYl'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

drive_service = build('drive', 'v3', credentials=credentials)



def start_watch(folder_id):
    watch_body = {
        'id': 'student-qb-images-upload-chnl',
        'type': 'webhook',
        'address': 'https://student-qb-be-t4m7k7vxoa-uc.a.run.app/file-uploaded',
    }
    drive_service.files().watch(fileId=folder_id, body=watch_body).execute()


start_watch(FOLDER_ID)