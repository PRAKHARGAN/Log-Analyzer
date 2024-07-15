import streamlit as st
from auth import show_login
from ui import main_app

def main():
    if show_login():
        main_app()

if __name__ == "__main__":
    main()
