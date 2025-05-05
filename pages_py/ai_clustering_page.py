import numexpr as ne
import streamlit as st
from datetime import time
import matplotlib.pyplot as plt
import seaborn as sns

from functions.clustering.feature_creation import create_feature_table
from utils.expanding_filter import ExpandingVisFilterAI

from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import silhouette_score

def make_histograms(df, X):
    unique_predict = sorted(df['predict_kmeans'].unique())

    # Set up the figure
    fig, axes = plt.subplots(1, len(unique_predict), figsize=(5 * len(unique_predict), 4), sharey=True)

    # If only one subplot, make sure axes is iterable
    if len(unique_predict) == 1:
        axes = [axes]

    # Create a histogram for each 'predict' value
    for i, predict_value in enumerate(unique_predict):
        subset = df[df['predict_kmeans'] == predict_value]
        sns.histplot(
            data=subset,
            x=X,
            bins=10,
            kde=False,
            ax=axes[i],
            stat="probability"
        )
        axes[i].set_title(f"Predict = {predict_value}")
        axes[i].set_xlabel(X)
        axes[i].set_ylabel("Relative frequency")

    # Adjust layout
    plt.tight_layout()
    return fig  # ⬅️ Return the figure instead of plt.show()

def make_colored_100_barchart(df, X):
    # Calculate proportions
    data = df.groupby([X, 'predict_kmeans']).size().reset_index(name='count')
    data['proportion'] = data.groupby(X)['count'].transform(lambda x: x / x.sum())

    # Pivot the data for plotting
    pivot_data = data.pivot(index=X, columns='predict_kmeans', values='proportion').fillna(0)

    # Plot the 100% stacked bar graph
    fig, ax = plt.subplots(figsize=(10, 6))
    pivot_data.plot(kind='bar', stacked=True, ax=ax)

    # Add labels and title
    ax.set_title(f"100% Stacked Bar Graph: {X}")
    ax.set_xlabel(X)
    ax.set_ylabel("Proportion")
    ax.legend(title="Predict", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()

    return fig

st.title("AI module - team structure analysis with clustering (T side)")

#st.header("Heatmaps - select map and matches")

filterer = ExpandingVisFilterAI()

if st.button("Perform Clustering"):
    df = create_feature_table(filterer.feed_match_idx())
    df = df[df['team_side']=='T']
    df['alive_time'] = df['alive_time']/df['round_time']
    features = df.drop(['name', 'team_name', 'match_name', 'team_side', 'team_equipment_value', 'enemy_equipment_value', 'round_num','round_won', 'round_time'], axis = 1).columns
    features = df.drop(['name', 'team_name', 'match_name', 'team_side', 'team_equipment_value', 'enemy_equipment_value', 'round_num','round_won', 'round_time', 'kill_participate_ratio', 'assist_participate_ratio','deaths_in_round','dmg_taken_in_round','hs_kill_count', 'kill_count', 'kill_count_team'], axis = 1).columns

    scaler = MinMaxScaler()
    df_scaled = scaler.fit_transform(df[features].fillna(0))

    kmeans_model = KMeans(n_clusters=5, random_state=42)

    df['predict_kmeans'] = kmeans_model.fit_predict(df_scaled)

    st.write('KMeans model with k=5 fit.')
    
    st.write(f'silhoutte_score: {round(silhouette_score(df_scaled, df['predict_kmeans']),2)}')

    inertia = []
    for k in range(2, 11):
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(df_scaled)
        inertia.append(kmeans.inertia_)

    fig, ax = plt.subplots()
    ax.plot(range(2, 11), inertia, marker='o')
    ax.set_xlabel('Number of clusters')
    ax.set_ylabel('Inertia')
    ax.set_title('Elbow method')

    with st.expander('Elbow method'):
        st.pyplot(fig, use_container_width=False)

    contin_features = [
    "dmg_in_round", "dmg_taken_in_round", "dmg_in_round_util",
    "engagement_count", "distance_travelled", "bomb_carried_ratio", "alive_time"]

    for c in contin_features:
        with st.expander(f"Histogram for {c}"):
            fig = make_histograms(df, c)
            st.pyplot(fig, use_container_width=False)

    discrete_features = [
        "round_won", "kills_in_round", "kill_count", "deaths_in_round", "entry_kill",
        "entry_damages", "round_survived", "attacking_util_threw", "supporting_util_threw",
        "last_alive_flag", "hs_kill_count", "kill_participate_ratio",
        "assist_participate_ratio", "awp_used_flag"
    ]

    for c in discrete_features:
        with st.expander(f"Stacked Bar Chart for {c}"):
            fig = make_colored_100_barchart(df, c)
            st.pyplot(fig, use_container_width=False)

    st.write(df)
