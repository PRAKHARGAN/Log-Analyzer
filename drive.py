from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import json
import base64
import os

def authenticate_gdrive(auth_code):
    flow = Flow.from_client_config(
        json.loads(base64.b64decode(os.environ['GOOGLE_CREDENTIALS']).decode('utf-8')),
        scopes=['https://www.googleapis.com/auth/drive'],
        redirect_uri='https://redwing-labs-log-analyzer.onrender.com/'
    )
    flow.fetch_token(code=auth_code)
    return build('drive', 'v3', credentials=flow.credentials)

def list_items(service, folder_id):
    results = service.files().list(q=f"'{folder_id}' in parents", fields="files(id, name)").execute()
    return results.get('files', [])
