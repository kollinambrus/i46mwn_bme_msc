import os
import pandas as pd
import streamlit as st
from streamlit_pills import pills
from awpy import Demo
#import awpy
#from awpy.stats import adr, kast, rating # will be calculated manually - because of multiple match source
import tempfile
import importlib.metadata
from HLTV import get_top_teams
from datetime import datetime, timedelta


from functions.add_sources import add_source, add_source_hltv
from functions.upload_config import handle_zip
from resources.hltv_parser.hltvparser import HLTVDemoParser

st.title("Upload data sources for analysis")

st.header("HLTV Scraping")

#st.write("TODO: implement HLTV Scraping")
with st.form("my_form", border=False):
    col1, col2 = st.columns(2)
    col1.selectbox("Game", ["CS2", "CS:GO"], disabled = True)
    match_type = col1.selectbox('Match type', ["LAN Only", "Online", "Both"])
    from_date = col1.date_input("From", value = datetime.today() - timedelta(days=7), max_value = datetime.today())
    stars = col2.selectbox('Stars', ["All", "1 or more","2 or more","3 or more","4 or more","5"])
    maps = col2.multiselect("Map",["All", "Inferno", "Mirage"], default = "All")
    to_date = col2.date_input("To", value = "today", min_value = from_date, max_value = datetime.today())
    if st.form_submit_button("Gather Matches"):
        st.session_state.hltv_parser = HLTVDemoParser(from_date, to_date, maps, match_type, stars)
        col3, col4 = st.columns(2)
        col3.selectbox("Team", get_top_teams())
        col4.selectbox("Event", ["1","2"])
        match_list = st.session_state.hltv_parser.gather_matches()
        st.write(match_list)
        #st.write(type(match_list))
        st.dataframe(pd.DataFrame({"Link to match": match_list}), use_container_width = True, hide_index = True, selection_mode="multi-row", on_select = "rerun", column_config = {"Link to match": st.column_config.LinkColumn("Link to match", help = "HLTV link of the match")})
        st.write(len(match_list))
        st.session_state.hltv_demo_ready_to_download = True
if st.session_state.hltv_demo_ready_to_download:
    if st.button("Process demos"):
        downloaded_dict = st.session_state.hltv_parser.download_demos()
        st.session_state.hltv_demo_ready_to_download = False
        files = os.listdir(os.path.abspath(os.path.join('.', 'DOWNLOADED_DIR')))
        for file in files:
            add_source_hltv(file, downloaded_dict[file])
            # st.write(st.session_state.data_dict["new_rating"])
#selected = pills("Label", ["Option 1", "Option 2", "Option 3a"], ["🍀", "🎈", "🌈"])
#st.write(selected)

st.header("Upload .dem file(s)")

dem_files = st.file_uploader("Upload .dem file(s)", type = ["dem"], accept_multiple_files=True, help = "You can only select CS2 .dem file(s)", key="dem")#type=[".dem"], 

if len(dem_files)>0:
    my_bar = st.progress(0, text = f"Parsing CS2 Demos... 0/{len(dem_files)}")
    step = 1/len(dem_files)
    progress_current_percent = 0
    progress_current_actual = 0
    for dem_file in dem_files:
        add_source(dem_file)
        progress_current_percent += step
        progress_current_actual += 1
        my_bar.progress(progress_current_percent, text = f"Parsing CS2 Demos... {progress_current_actual}/{len(dem_files)}")
    # st.write(st.session_state.data_dict["new_rating"])
    #if len(st.session_state.data_dict["ticks"])>0: st.write(st.session_state.data_dict["ticks"])
    #st.write(len(st.session_state.data_dict["ticks"]))
else:
    st.info('☝️ Upload the .dem file(s) here')

st.header("Upload CS: Analytics config(s)")

zip_files = st.file_uploader("Upload CS: Analytics config(s)", type = ["zip"], accept_multiple_files=True, help = "You can only select .zip file(s)", key="zip")

if len(zip_files) > 0:
    if handle_zip(zip_files):
        st.success("Processing uploaded ZIP file(s) done.")
else:
    st.info('☝️ Upload the .zip file(s) here')


