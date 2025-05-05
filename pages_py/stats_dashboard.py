import numpy as np
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from utils.expanding_filter import ExpandingVisFilterDashBoard
from streamlit_pills import pills

def create_dashboard(expanding_filter: ExpandingVisFilterDashBoard):
    expanding_filter.create_filter()
    match_idx = expanding_filter.feed_match_idx()
    player_stats = st.session_state.stats_df.query(expanding_filter.query_text)
    average_stats = st.session_state.stats_df.query(expanding_filter.for_average_query)

    # Placeholder KPIs (replace these with actual filtered data)
    kills = player_stats["kills"].sum() / len(filterer.player_name)
    death = player_stats["deaths"].sum() / len(filterer.player_name)
    kd_ratio = player_stats["kills"].sum() / player_stats["deaths"].sum()
    n_rounds = player_stats["n_rounds"].sum() / len(filterer.player_name)
    adr_av = np.sum(player_stats["adr"] * player_stats["n_rounds"]) / player_stats["n_rounds"].sum()
    kast_av = np.sum(player_stats["kast"] * player_stats["n_rounds"]) / player_stats["n_rounds"].sum()
    impact_av = np.sum(player_stats["impact"] * player_stats["n_rounds"]) / player_stats["n_rounds"].sum()
    rating_av = np.sum(player_stats["rating"] * player_stats["n_rounds"]) / player_stats["n_rounds"].sum()

    kills_average = average_stats["kills"].sum() / average_stats['name'].nunique()
    death_average = average_stats["deaths"].sum() / average_stats['name'].nunique()
    kd_ratio_average = kills_average / death_average
    n_rounds_average = average_stats["n_rounds"].sum() / average_stats['name'].nunique()
    adr_av_average = np.sum(average_stats["adr"] * average_stats["n_rounds"]) / average_stats["n_rounds"].sum()
    kast_av_average = np.sum(average_stats["kast"] * average_stats["n_rounds"]) / average_stats["n_rounds"].sum()
    impact_av_average = np.sum(average_stats["impact"] * average_stats["n_rounds"]) / average_stats["n_rounds"].sum()
    rating_av_average = np.sum(average_stats["rating"] * average_stats["n_rounds"]) / average_stats["n_rounds"].sum()

    st.markdown("---")
    # Top KPIs
    col1, col2, col3, col4 = st.columns(4)
    # st.write(st.session_state.stats_df)
    col1.metric("Kills", f"{kills:.0f}", int(kills - kills_average))
    col2.metric("Death", f"{death:.0f}", int(death_average - death))
    col3.metric("K/D Ratio", f"{kd_ratio:.2f}", round(float(kd_ratio - kd_ratio_average),2))
    col4.metric("Rounds Played", f"{n_rounds:.0f}", round(float(n_rounds - n_rounds_average),2))
    col1.metric("ADR", f"{adr_av:.1f}", round(float(adr_av - adr_av_average),2))
    col2.metric("KAST %", f"{kast_av:.1f}%", f"{round(float(kast_av - kast_av_average),2)}%")
    col3.metric("Impact", f"{impact_av:.2f}", round(float(impact_av - impact_av_average),2))
    col4.metric("Rating", f"{rating_av:.2f}", round(float(rating_av - rating_av_average),2))

    st.markdown("---")

    side_filter = "TERRORIST" if expanding_filter.side_name == "T" else "all" if expanding_filter.side_name == "Both" else "CT"
    stat_table = st.session_state.stats_df[(st.session_state.stats_df["match_src"].isin(match_idx))&(st.session_state.stats_df["team_name"] == side_filter)].sort_values(by=["match_src", "team_name"], ascending=True)[["name", "map_name", "team_name", "n_rounds", "kast", "adr", "impact", "kills", "deaths", "rating", "kdr"]]
    st.dataframe(stat_table, 
                 use_container_width=True, hide_index=True,
                 column_config={
                    "rating": st.column_config.ProgressColumn(
                        "rating",
                        format="%.2f",
                        min_value=0,
                        max_value=max(stat_table["rating"]),),
                        "kdr": st.column_config.ProgressColumn(
                        "kdr",
                        format="%.2f",
                        min_value=0,
                        max_value=max(stat_table["rating"])),
                        })

    # Simulated sample data (replace with real data)
    kills_by_round = pd.DataFrame({
        "Round": list(range(1, 11)),
        "Kills": [2, 3, 4, 5, 3, 4, 5, 4, 4, 5]
    })

    # Filter to the selected side
    side_df = st.session_state.stats_df[st.session_state.stats_df["team_name"] == side_filter]

    # Group by player name and sum kills
    kills_by_player = side_df.groupby("name")["kills"].sum().reset_index()

    # Calculate total kills for percentage
    total_kills = kills_by_player["kills"].sum()

    # Add percentage column
    kills_by_player["kill_pct"] = (kills_by_player["kills"] / total_kills) * 100

    # Optional: sort by kills descending
    kills_by_player = kills_by_player.sort_values("kills", ascending=False)

    kills_by_game_state = pd.DataFrame({
        "Game State": ["Man Advantage", "Even", "Man Disadvantage"],
        "Kills": [20, 15, 10],
        "Deaths": [10, 10, 20]
    })

    # Layout for charts
    col5, col6 = st.columns(2)

    # # Kills by Round (Bar Chart)
    # with col5:
    #     st.subheader("Rating by Side and Map")
    #     fig, ax = plt.subplots()
    #     ax.bar(kills_by_round["Round"], kills_by_round["Kills"], color="#3399ff")
    #     ax.set_xlabel("Round")
    #     ax.set_ylabel("Kills")
    #     st.pyplot(fig)

    df = st.session_state.stats_df[(st.session_state.stats_df["match_src"].isin(match_idx))&(st.session_state.stats_df["name"].isin(filterer.player_name))]

    # Define a function for weighted average
    def weighted_avg(group):
        return (group["rating"] * group["n_rounds"]).sum() / group["n_rounds"].sum()

    # Group by map_name and team_name, then apply weighted average
    weighted_ratings = (
        df.groupby(["map_name", "team_name"])
        .apply(weighted_avg)
        .reset_index(name="weighted_rating")
    )

    # Optional: sort or round
    weighted_ratings["weighted_rating"] = weighted_ratings["weighted_rating"].round(3)

    # Display result
    #st.dataframe(weighted_ratings, use_container_width=True)
    with col5:
        st.subheader("Weighted Player Rating per Map per Side")
        fig = px.bar(
            weighted_ratings,
            x="map_name",
            y="weighted_rating",
            color="team_name",
            barmode="group",  # options: 'group', 'stack'
            # title="Weighted Player Rating per Map per Side",
            labels={
                "map_name": "Map",
                "weighted_rating": "Weighted Rating",
                "team_name": "Team"
            },
            text_auto=".2f",  # show values on bars
            height=500
        )

        # Optional tweaks
        fig.update_layout(
            xaxis_title="Map",
            yaxis_title="Weighted Rating",
            legend_title="Team",
            bargap=0.2
        )

        # Display it
        st.plotly_chart(fig, use_container_width=True)

    # KPIs by Buy Type (Pie Chart)
    with col6:
        st.subheader("Kill distribution on selected matches")
        fig = px.pie(kills_by_player, names="name", values="kill_pct", hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(fig)

    # Kills by Game State (Stacked Bar)
    # st.subheader("Kills per player")
    # kills_state_df = kills_by_game_state.set_index("Game State")
    # fig, ax = plt.subplots()
    # kills_state_df.plot(kind='barh', stacked=True, ax=ax, color=["#1f77b4", "#ff7f0e"])
    # ax.set_xlabel("Count")
    # st.pyplot(fig)



# Page setup
# st.set_page_config(page_title="CS2 Web App Dashboard", layout="wide")
st.title("Stats Module - Dashboard")

filterer = ExpandingVisFilterDashBoard()

if st.button("Generate Dashboard"):
    create_dashboard(filterer)
st.markdown("---")