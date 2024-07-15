import streamlit as st

# Dummy credentials for login
USERNAME = "user"
PASSWORD = "pass"

def login(username, password):
    if username == USERNAME and password == PASSWORD:
        return True
    else:
        return False

def show_login():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.title('Login')
        username = st.text_input('Username')
        password = st.text_input('Password', type='password')
        if st.button('Login'):
            if login(username, password):
                st.session_state.logged_in = True
                st.experimental_rerun()
            else:
                st.error('Invalid credentials')
        return False
    return True
