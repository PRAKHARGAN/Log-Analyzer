import streamlit as st
from drive import authenticate_gdrive, list_items

def main_app(service):
    st.title('Log Analyzer')

    root_folder_id = '1dOD1aA8HWB9Rjus7nG9Phld3LjoZ6YZG'  # Replace with your root folder ID
    folders = list_items(service, root_folder_id, 'application/vnd.google-apps.folder')
    st.write(f'Folders: {folders}')

def main():
    query_params = st.experimental_get_query_params()
    auth_code = query_params.get('code', [None])[0]

    if 'service' not in st.session_state:
        if auth_code:
            service = authenticate_gdrive(auth_code)
            st.session_state.service = service
            st.experimental_rerun()
        else:
            auth_url = authenticate_gdrive()
            st.write(f'Please go to the following URL to authenticate: [Authenticate here]({auth_url})')

    if 'service' in st.session_state:
        main_app(st.session_state.service)

if __name__ == "__main__":
    main()
