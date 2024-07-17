# drive.py
import os
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

# OAuth 2.0 setup
SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate_gdrive():
    creds = None
    token_path = 'token.pickle'

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0, open_browser=False)
        auth_url, _ = flow.authorization_url(prompt='consent')

        print(f'Please go to this URL: {auth_url}')

        code = input('Enter the authorization code: ')
        flow.fetch_token(code=code)

        creds = flow.credentials

        with open(token_path, 'wb') as token:
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
