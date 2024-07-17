# ui.py
import streamlit as st
import os
from drive import authenticate_gdrive, list_items, download_file
from log_analysis import detect_flight_phases


def main_app():
    st.title('Log Analyzer')

    service = authenticate_gdrive()

    root_folder_id = '1dOD1aA8HWB9Rjus7nG9Phld3LjoZ6YZG'  # Replace with your actual root folder ID
    folders = list_items(service, root_folder_id, 'application/vnd.google-apps.folder')
    folder_names = [folder['name'] for folder in folders]
    folder_ids = {folder['name']: folder['id'] for folder in folders}
    selected_folder = st.selectbox("Select a folder from Logs", folder_names)

    if selected_folder:
        selected_folder_id = folder_ids[selected_folder]
        subfolders = list_items(service, selected_folder_id, 'application/vnd.google-apps.folder')
        subfolder_names = [subfolder['name'] for subfolder in subfolders]
        subfolder_ids = {subfolder['name']: subfolder['id'] for subfolder in subfolders}
        selected_subfolder = st.selectbox("Select a subfolder", subfolder_names)

        if selected_subfolder:
            selected_subfolder_id = subfolder_ids[selected_subfolder]
            files = list_items(service, selected_subfolder_id, None)  # List all files in subfolder
            file_names = [file['name'] for file in files]
            file_ids = {file['name']: file['id'] for file in files}
            selected_file = st.selectbox("Select a file", file_names)

            if selected_file:
                file_id = file_ids[selected_file]
                st.write(f'You selected: {selected_folder}/{selected_subfolder}/{selected_file}')

                if st.button('Analyze the Log'):
                    try:
                        # Download the file to a temporary location
                        local_file_path = download_file(service, file_id, 'LOG.bin')

                        if local_file_path:
                            # Analyze the downloaded file
                            phases = detect_flight_phases(local_file_path)

                            # Display analysis results
                            st.write("Flight Phases Detected:")
                            for phase in phases:
                                st.write(f"Phase: {phase[0]}, Energy Consumed (Wh): {phase[1]}, "
                                         f"Distance Traveled (m): {phase[2]}, Altitude (m): {phase[3]}, Whr/Km: {phase[4]}")

                            # Clean up: Delete the temporary file
                            os.remove(local_file_path)
                        else:
                            st.error("Failed to download the file. Please try again.")

                    except Exception as e:
                        st.error(f"An error occurred during analysis: {e}")

    if st.button('Reauthorize'):
        if os.path.exists('token.pickle'):
            os.remove('token.pickle')
        st.write('Please restart the application to reauthorize.')
