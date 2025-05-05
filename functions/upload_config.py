import pandas as pd
import streamlit as st
import zipfile
import io

def validate_zip(zip_files, expected_files = ["bomb.data", "config.data", "damages.data", "grenades.data", "infernos.data", "kills.data", "rounds.data", "smokes.data", "ticks.data", "weapon_fires.data"]):
    """
    Validates that the ZIP file contains exactly the expected files.
    
    Args:
        zip_files (list): List of file names in the ZIP archive.
        expected_files (list): List of the expected files. Set by default.
    
    Returns:
        bool: True if the ZIP file contains exactly the expected files, False otherwise.
    """
    return sorted(zip_files) == sorted(expected_files)

def process_zip(zip_file: zipfile.ZipFile):
    """
    Processes the contents of the ZIP file by reading each file, loading it into a pandas DataFrame,
    and concatenating it with the corresponding DataFrame in st.session_state['data_dict'].

    Args:
        zip_file (zipfile.ZipFile): The opened ZIP file object.

    Returns:
        None
    """
    # Iterate over the files in the ZIP archive
    for file_name in zip_file.namelist():
        # Remove the file extension to get the key (assuming '.data' extension)
        key = file_name.replace('.data', '')

        # Check if the key exists in st.session_state['data_dict']
        if key in st.session_state['data_dict']:
            # Read the file into a pandas DataFrame
            with zip_file.open(file_name) as file:
                new_df = pd.read_parquet(file)  # Assuming the file is CSV. Adjust accordingly if different.

            # Concatenate with the existing DataFrame in session state
            st.session_state['data_dict'][key] = pd.concat([st.session_state['data_dict'][key], new_df], ignore_index = True)

            #st.success(f"{file_name} has been successfully processed and concatenated.")
        elif key == 'config':
            with zip_file.open(file_name) as file:
                new_df = pd.read_parquet(file)  # Assuming the file is CSV. Adjust accordingly if different.
            st.session_state.dem_list = pd.concat([st.session_state.dem_list, new_df], ignore_index = True)
            #st.success(f"{file_name} has been successfully processed and concatenated.")
        #else:
            #st.warning(f"No corresponding key found in st.session_state['data_dict'] for {file_name}.")
            

def handle_zip(uploaded_files: list):
    """
    Handles the uploaded ZIP file by validating and processing it.
    
    Args:
        uploaded_file (UploadedFile): The uploaded ZIP file from Streamlit.
    
    Returns:
        bool: True if the ZIP file contains exactly the expected files, False otherwise.
    """
    for uploaded_file in uploaded_files:
        with zipfile.ZipFile(io.BytesIO(uploaded_file.read())) as z:
            # Get the list of files in the ZIP archive
            zip_files = z.namelist()

            # Validate the ZIP file
            if validate_zip(zip_files):
                # Process the ZIP file
                process_zip(z)
                return True
            else:
                st.error("The ZIP file does not contain the correct set of files.")
                st.write("Expected files:")
                st.write(sorted(["bomb.data", "config.data", "damages.data", "grenades.data", "infernos.data", "kills.data", "rounds.data", "smokes.data", "ticks.data", "weapon_fires.data"]))
                st.write("Files in the ZIP:")
                st.write(sorted(zip_files))
                return False