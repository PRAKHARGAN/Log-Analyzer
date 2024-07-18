# app.py
import streamlit as st
from drive import authenticate_gdrive

def main():
    st.title("Google Drive Authentication")

    # Check if the user is already authenticated
    if 'service' not in st.session_state:
        auth_code = st.experimental_get_query_params().get('code')

        if auth_code:
            st.session_state.service = authenticate_gdrive(auth_code)
            st.success("Successfully authenticated with Google Drive!")
        else:
            auth_url = authenticate_gdrive()
            if auth_url:
                st.write(f"[Authenticate here]({auth_url})")
            else:
                st.error("Unable to generate authentication URL. Please try again later.")

    # Continue with your app logic
    if 'service' in st.session_state:
        service = st.session_state.service
        # Your app logic here
        st.write("Your app logic here.")

if __name__ == '__main__':
    main()
