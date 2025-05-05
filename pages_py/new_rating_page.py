import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

from utils.expanding_filter import ExpandingVisFilterNewRating

def show_ratings(expanding_filter: ExpandingVisFilterNewRating):
    expanding_filter.create_filter()
    match_idx = expanding_filter.feed_match_idx()
    ticks = st.session_state.data_dict['new_rating'].query(expanding_filter.query_text)

    # fig.suptitle("Your Heatmap Title", fontsize=16)
    st.write(expanding_filter.query_text)
    # st.write(fig,ax)
    rating_series = ticks['Rating'].dropna()

    # Count unique values
    unique_values = rating_series.nunique()

    if unique_values > 0:

        # Define color palettes
        side_colors = {'TERRORIST': '#FFD700', 'CT': '#3498db'}
        team_colors = dict(zip(ticks['team_clan_name'].unique(), sns.color_palette("Set2").as_hex()))
        economy_colors = dict(zip(ticks['PlayerEconomy'].unique(), sns.color_palette("Set3").as_hex()))
        player_colors = dict(zip(ticks['Player'].unique(), sns.color_palette("tab10").as_hex()))

        # Plot 1: No grouping (Full-width top)
        st.subheader("Rating Distribution (No Grouping)")
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(ticks['Rating'], bins=20, color='gray', edgecolor='black')
        ax.set_title("Rating Distribution (No Grouping)")
        ax.set_xlabel("Rating")
        ax.set_ylabel("Frequency")
        st.pyplot(fig)

        # Define grouped plots
        groupings = [
            ('Player', player_colors, 'Rating Distribution by Player'),
            ('PlayerSide', side_colors, 'Rating Distribution by Player Side'),
            ('PlayerEconomy', economy_colors, 'Rating Distribution by Player Economy'),
            ('team_clan_name', team_colors, 'Rating Distribution by Team'),
        ]

        # Create 2x2 grid
        for i in range(0, len(groupings), 2):
            col1, col2 = st.columns(2)
            
            for col, (group_col, color_dict, title) in zip([col1, col2], groupings[i:i+2]):
                with col:
                    fig, ax = plt.subplots(figsize=(6, 4))
                    for group in ticks[group_col].unique():
                        subset = ticks[ticks[group_col] == group]
                        ax.hist(subset['Rating'], bins=20, alpha=0.6,
                                label=group, color=color_dict.get(group, 'gray'))
                    ax.set_title(title)
                    ax.set_xlabel("Rating")
                    ax.set_ylabel("Frequency")
                    ax.legend(title=group_col)
                    st.pyplot(fig, use_container_width=False)
        st.write(ticks)

st.title("New Rating module")

st.header("Analyze New Rating values based on different features")
#st.write(st.session_state.data_dict["new_rating"])
filterer = ExpandingVisFilterNewRating()

if st.button("Show New Ratings"):
    show_ratings(filterer)
    # st.write(st.session_state.data_dict["rounds"])
# st.write(st.session_state.data_dict["new_rating"])