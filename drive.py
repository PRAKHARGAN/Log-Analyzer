# drive.py
import os
import pickle
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

# OAuth 2.0 setup
SCOPES = ['https://www.googleapis.com/auth/drive']
TOKEN_PATH = 'token.pickle'
CREDENTIALS_PATH = 'credentials.json'

# Function to authenticate Google Drive
def authenticate_gdrive(auth_code=None):
    creds = None

    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        flow = Flow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
        flow.redirect_uri = 'https://redwing-labs-log-analyzer.onrender.com/'  # Ensure correct redirect URI

        if auth_code:
            flow.fetch_token(code=auth_code)

        else:
            auth_url, _ = flow.authorization_url(prompt='consent')

            return auth_url  # Return the URL for the user to visit

    service = build('drive', 'v3', credentials=creds)
    return service
