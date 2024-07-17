# drive.py
import os
import pickle
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

# OAuth 2.0 setup
SCOPES = ['https://www.googleapis.com/auth/drive']
TOKEN_PATH = 'token.pickle'
CREDENTIALS_PATH = 'credentials.json'

def authenticate_gdrive(auth_code=None):
    creds = None

    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        flow = Flow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
        flow.redirect_uri = 'https://your-app.onrender.com'  # Use your deployed URL

        if auth_code is None:
            auth_url, _ = flow.authorization_url(prompt='consent')
            return auth_url  # Return the URL for the user to visit

        flow.fetch_token(code=auth_code)
        creds = flow.credentials

        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    return service

def list_items(service, folder_id='root', mime_type=None):
    query = f"'{folder_id}' in parents"
    if mime_type:
        query += f" and mimeType = '{mime_type}'"
    try:
        results = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name, mimeType)'
        ).execute()
        items = results.get('files', [])
        return items
    except Exception as e:
        print(f"An error occurred while listing items: {e}")
        return []

def download_file(service, file_id, file_name):
    try:
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()

        with open(file_name, 'wb') as f:
            fh.seek(0)
            f.write(fh.read())

        return file_name

    except Exception as e:
        print(f"An error occurred during download: {e}")
        return None
