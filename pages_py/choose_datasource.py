import os
import zipfile
import numpy as np
import pandas as pd
import streamlit as st
from streamlit_pills import pills
from awpy import Demo
import awpy
#from awpy.stats import adr, kast, rating # will be calculated manually - because of multiple match source
import tempfile
import importlib.metadata
from datetime import datetime

def format_excluded_demo(row):
    return ['background-color: rgba(140, 140, 140, 10);'] * len(row) if row['include/exclude/delete'] == 'Exclude' else [None] * len(row)

@st.cache_data
def convert_df(df: pd.DataFrame):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(sep='|', index = False).encode("utf-8")

@st.cache_data
def create_downloadable_zip(data_dict: dict, config_df: pd.DataFrame):
    # Create a temporary directory to store parquet files
    with tempfile.TemporaryDirectory() as tempdir:
        # handle large df with data
        parquet_paths = []
        file_names = []
        for key_c in data_dict.keys():
            if key_c != 'header':
                path_c = os.path.join(tempdir, f'{key_c}.data')
                data_dict[key_c].to_parquet(path_c)
                parquet_paths.append(path_c)
                file_names.append(key_c)

        #handle config
        path_c = os.path.join(tempdir, 'config.data')
        config_df.to_parquet(path_c)
        parquet_paths.append(path_c)
        file_names.append('config')
        
        # Create a ZIP file containing the Parquet files
        zip_path = os.path.join(tempdir, 'dataframes.zip')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for path, name in zip(parquet_paths, file_names):
                zipf.write(path, f'{name}.data')
        
        # Read the ZIP file as bytes
        with open(zip_path, 'rb') as f:
            zip_bytes = f.read()
    
    return zip_bytes

st.title("Choose data sources for analysis")

# df = pd.DataFrame(
#     [
#         {"command": "st.selectbox", "rating": 4, "is_widget": True},
#         {"command": "st.balloons", "rating": 5, "is_widget": False},
#         {"command": "st.time_input", "rating": 3, "is_widget": True},
#     ]
# )
# edited_df = st.dataframe(
#     df,
#     column_config={
#         "command": "Streamlit Command",
#         "rating": st.column_config.NumberColumn(
#             "Your rating",
#             help="How much do you like this command (1-5)?",
#             min_value=1,
#             max_value=5,
#             step=1,
#             format="%d ⭐",
#         ),
#         "is_widget": "Widget ?",
#     },
#     #disabled=["command", "is_widget"],
#     #hide_index=True,
#     selection_mode="multi-row",
#     on_select = "rerun"
# )

#st.session_state.dem_list = st.data_editor(

new_df = st.dataframe(
    st.session_state.dem_list.style.apply(format_excluded_demo, axis = 1),
    column_order = ("map", "team1", "team2", "score","source","match_page","include/exclude/delete"),
    column_config = {
        "map": st.column_config.ImageColumn(
            "Map", help="Map", width="small"
        ),
        "team1": st.column_config.Column("Team 1", disabled = True),
        "team2": st.column_config.Column("Team 2", disabled = True),
        "score": st.column_config.Column("Score", disabled = True),
        "source": st.column_config.Column("Source", disabled = True),
        "match_page": st.column_config.LinkColumn("Match page", help = "You can update with HLTV link for uploaded .dem files"),
        "include/exclude/delete": st.column_config.SelectboxColumn(
            "Include?",
            help="Decide if match should be analysed",
            width="medium",
            options=[
                "Include",
                "Exclude",
                "Delete",
            ],
            required=True,
        )
    },
    hide_index = True,
    selection_mode="multi-row",
    on_select = "rerun",
    use_container_width = True
)

#favorite_command = edited_df.loc[edited_df["rating"].idxmax()]["command"]
#st.markdown(f"Your favorite command is **{favorite_command}** 🎈")
col1, col2, col3, col4 = st.columns(4)
if col1.button("Exclude selected...", use_container_width = True):
    st.session_state.dem_list.iloc[new_df.selection.rows, 8] = 'Exclude'
    st.rerun()
if col2.button("Include selected...", use_container_width = True):
    st.session_state.dem_list.iloc[new_df.selection.rows, 8] = 'Include'
    st.rerun()
if col4.button("Remove selected...", use_container_width = True):
    ids_to_delete = list(st.session_state.dem_list.iloc[new_df.selection.rows, 7].unique())
    st.session_state.dem_list = st.session_state.dem_list[~st.session_state.dem_list['file_id'].isin(ids_to_delete)]

    for key in st.session_state.data_dict.keys():
        if key != 'header':
            st.session_state.data_dict[key] = st.session_state.data_dict[key][~st.session_state.data_dict[key]['match_src'].isin(ids_to_delete)]
    st.session_state.data_dict["header"] = [item for item in st.session_state.data_dict["header"] if item["match_src"] not in ids_to_delete]

    st.rerun()

#st.download_button("Download data and settings", data = convert_df(st.session_state.data_dict["ticks"]), file_name = "my_file.csv", help = "xd mi a szatyor")
#download_checkbox = st.checkbox('Check here to download parsed demos and the configuration')
#if download_checkbox:
st.divider()
col5, col6, col7, col8, col9, col10, col11, col12 = st.columns(8)
#col12.button('Upload previously downloaded ZIP', use_container_width = True)
col5.download_button("Download data and settings", data = create_downloadable_zip(st.session_state.data_dict, st.session_state.dem_list), file_name = f"cs_analytics_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip", help = "xd mi a szatyor")





