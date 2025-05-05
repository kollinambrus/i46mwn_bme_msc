import numexpr as ne
import streamlit as st
from datetime import time
from awpy.plot import heatmap
import matplotlib.pyplot as plt
from awpy.plot import gif, PLOT_SETTINGS
import tempfile
import pathlib
from tqdm import tqdm

from utils.expanding_filter import ExpandingVisFilterReplay

def create_and_display_gif(expanding_filter: ExpandingVisFilterReplay):
    expanding_filter.create_filter()
    match_idx = expanding_filter.feed_match_idx()
    ticks = st.session_state.data_dict['ticks'].query(expanding_filter.query_text)
    frames = []

    good_ticks = ticks
    good_ticks['team_name'] = good_ticks['team_name'].str.replace('TERRORIST', 't').replace('CT', 'ct')

    #for tick in tqdm(good_ticks.query("round == 10")["tick"].unique()[::64]):
    #for tick in tqdm(good_ticks.query("round == 10")["tick"][::128]):
    for tick in tqdm(good_ticks["tick"][::128]):
        frame_df = good_ticks.query(f"tick == {tick}")
        frame_df = frame_df[
            ["X", "Y", "Z", "health", "armor_value", "pitch", "yaw", "team_name", "name"]
        ]

        points = []
        point_settings = []

        for row in frame_df.itertuples(index=False, name=None):
            points.append((row[0], row[1], row[2]))

            # Determine team and corresponding settings
            settings = PLOT_SETTINGS[row[7]].copy()

            # Add additional settings
            settings.update(
                {
                    "hp": row[3],
                    "armor": row[4],
                    "direction": (row[5], row[6]),
                    "label": row[8],
                }
            )

            point_settings.append(settings)

        frames.append({"points": points, "point_settings": point_settings})

    # Use a temporary directory to save and show the gif
    with tempfile.TemporaryDirectory() as tmp_dir:
        gif_path = pathlib.Path(tmp_dir) / "demo.gif"
        
        # Create the GIF
        gif(expanding_filter.feed_match_map(), frames, str(gif_path), duration=100)
        
        # Display in Streamlit
        st.image(str(gif_path), caption="Round Overview", use_container_width ="auto")



st.title("Visualisation module - replay")

st.header("Replay - select map, match and round number")

filterer = ExpandingVisFilterReplay()

with st.expander("Plot settings"):
    st.write("Coming sooon")

if st.button("Generate Replay"):
    create_and_display_gif(filterer)





