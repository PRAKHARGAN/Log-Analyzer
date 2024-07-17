# app.py
import streamlit as st
from drive import authenticate_gdrive
from ui import main_app
from auth import show_login

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
        if show_login():
            main_app(st.session_state.service)

if __name__ == "__main__":
    main()
