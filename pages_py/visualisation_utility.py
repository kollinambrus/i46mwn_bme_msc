import numexpr as ne
import streamlit as st
from datetime import time
from awpy.plot import heatmap
import matplotlib.pyplot as plt

from utils.expanding_filter import ExpandingVisFilterUtility

def generate_heatmap(expanding_filter: ExpandingVisFilterUtility):
    expanding_filter.create_filter()
    match_idx = expanding_filter.feed_match_idx()
    print(expanding_filter.query_text)
    ticks = st.session_state.data_dict['grenades'].query(expanding_filter.query_text)
    ticks = ticks.groupby("entity_id").tail(1).reset_index()

    ticks = ticks[(~ticks['thrower'].isna()) & (~ticks['X'].isna()) & (~ticks['Y'].isna()) & (~ticks['Z'].isna())]

    player_locations = list(
    ticks[["X", "Y", "Z"]].itertuples(index=False, name=None)
)
    fig, ax = heatmap(map_name=expanding_filter.feed_match_map(), points=player_locations, method="hex", size=30) #  method = 'hex', 'hist', 'kde'
    # fig.suptitle("Your Heatmap Title", fontsize=16)
    st.write(expanding_filter.query_text)
    st.pyplot(fig, use_container_width=False)
    # st.write(fig,ax)
    # st.write(ticks.head())



st.title("Visualisation module - utility")

st.header("Heatmaps - select map and matches")

filterer = ExpandingVisFilterUtility()

with st.expander("Plot settings"):
    st.write("Coming sooon")

if st.button("Generate Heatmap"):
    generate_heatmap(filterer)
    #st.write(st.session_state.data_dict["rounds"])
