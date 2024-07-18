import streamlit as st
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import os
import json
import base64

# Function to authenticate and build the Google Drive service
def authenticate_gdrive():
    if 'credentials' not in st.session_state:
        st.write("Please authenticate to proceed.")
        auth_code = st.text_input('Enter the authorization code:', '')
        if st.button('Submit Code'):
            flow = Flow.from_client_config(
                json.loads(base64.b64decode(os.environ['GOOGLE_CREDENTIALS']).decode('utf-8')),
                scopes=['https://www.googleapis.com/auth/drive'],
                redirect_uri='https://redwing-labs-log-analyzer.onrender.com/'
            )
            flow.fetch_token(code=auth_code)
            credentials = flow.credentials
            st.session_state.credentials = credentials
            st.success('Successfully authenticated with Google Drive!')
    else:
        credentials = st.session_state.credentials

    return build('drive', 'v3', credentials=credentials)

# Function to list items in a specified Google Drive folder
def list_items(service, folder_id):
    results = service.files().list(q=f"'{folder_id}' in parents", fields="files(id, name)").execute()
    return results.get('files', [])

# Main function to run the Streamlit app
def main():
    st.title("Google Drive File Explorer")

    service = authenticate_gdrive()

    if 'credentials' in st.session_state:
        st.write("Successfully authenticated! You can now interact with Google Drive.")

        folder_id = st.text_input('Enter Google Drive folder ID:', '')
        if st.button('List Files'):
            items = list_items(service, folder_id)
            if not items:
                st.write('No files found.')
            else:
                for item in items:
                    st.write(f'{item["name"]} (ID: {item["id"]})')

if __name__ == '__main__':
    main()
