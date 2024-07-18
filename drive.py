# drive.py
import os
import pickle
import base64
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

# OAuth 2.0 setup
SCOPES = ['https://www.googleapis.com/auth/drive']
TOKEN_PATH = 'token.pickle'
CREDENTIALS_PATH = 'credentials.json'

# Decode the Base64 credentials and write to 'credentials.json'
base64_credentials = os.getenv('GOOGLE_CREDENTIALS_BASE64')
if base64_credentials:
    with open(CREDENTIALS_PATH, 'wb') as f:
        f.write(base64.b64decode(base64_credentials))

def authenticate_gdrive(auth_code=None):
    creds = None

    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        flow = Flow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
        flow.redirect_uri = 'https://redwing-labs-log-analyzer.onrender.com/'  # Update to match the one in Google Cloud Console

        if auth_code:
            flow.fetch_token(code=auth_code)
            creds = flow.credentials

            # Save the credentials for the next run
            with open(TOKEN_PATH, 'wb') as token:
                pickle.dump(creds, token)
        else:
            auth_url, _ = flow.authorization_url(prompt='consent')
            return auth_url  # Return the URL for the user to visit

    service = build('drive', 'v3', credentials=creds)
    return service

# Function to list items in a folder
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

# Function to download a file
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
