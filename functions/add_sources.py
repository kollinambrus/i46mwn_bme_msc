import tempfile
import zipfile
from awpy import Demo
import pandas as pd
import streamlit as st
import os
import rarfile
from .new_rating import func
from awpy.stats import adr, calculate_trades, impact, kast
from awpy.stats.utils import get_player_rounds


def rating2(demo: Demo) -> pd.DataFrame:
    """Calculates player rating, similar to HLTV.

    Args:
        demo (Demo): A parsed Awpy demo.

    Returns:
        pd.DataFrame: A dataframe of the player info + impact + rating.

    Raises:
        ValueError: If kills or ticks are missing in the parsed demo.
    """
    if demo.kills is None:
        missing_kills_error_msg = "Kills is missing in the parsed demo!"
        raise ValueError(missing_kills_error_msg)

    if demo.ticks is None:
        missing_ticks_error_msg = "Ticks is missing in the parsed demo!"
        raise ValueError(missing_ticks_error_msg)

    # Get total rounds by player
    player_total_rounds = get_player_rounds(demo)

    # Get deaths and assists
    kills_total = (
        demo.kills.groupby(["attacker_name", "attacker_steamid"])
        .size()
        .reset_index(name="kills")
        .rename(columns={"attacker_name": "name", "attacker_steamid": "steamid"})
    )
    kills_total["team_name"] = "all"
    kills_ct = (
        demo.kills[demo.kills["attacker_team_name"] == "CT"]
        .groupby(["attacker_name", "attacker_steamid"])
        .size()
        .reset_index(name="kills")
        .rename(columns={"attacker_name": "name", "attacker_steamid": "steamid"})
    )
    kills_ct["team_name"] = "CT"
    kills_t = (
        demo.kills[demo.kills["attacker_team_name"] == "TERRORIST"]
        .groupby(["attacker_name", "attacker_steamid"])
        .size()
        .reset_index(name="kills")
        .rename(columns={"attacker_name": "name", "attacker_steamid": "steamid"})
    )
    kills_t["team_name"] = "TERRORIST"
    kills = pd.concat([kills_total, kills_ct, kills_t])

    deaths_total = (
        demo.kills.groupby(["victim_name", "victim_steamid"])
        .size()
        .reset_index(name="deaths")
        .rename(columns={"victim_name": "name", "victim_steamid": "steamid"})
    )
    deaths_total["team_name"] = "all"
    deaths_ct = (
        demo.kills[demo.kills["victim_team_name"] == "CT"]
        .groupby(["victim_name", "victim_steamid"])
        .size()
        .reset_index(name="deaths")
        .rename(columns={"victim_name": "name", "victim_steamid": "steamid"})
    )
    deaths_ct["team_name"] = "CT"
    deaths_t = (
        demo.kills[demo.kills["victim_team_name"] == "TERRORIST"]
        .groupby(["victim_name", "victim_steamid"])
        .size()
        .reset_index(name="deaths")
        .rename(columns={"victim_name": "name", "victim_steamid": "steamid"})
    )
    deaths_t["team_name"] = "TERRORIST"
    deaths = pd.concat([deaths_total, deaths_ct, deaths_t])

    # KAST/ADR/Impact
    kast_df = kast(demo)
    adr_df = adr(demo)
    impact_df = impact(demo)

    # Merge and calculate
    rating_df = (
        player_total_rounds.merge(
            kast_df[["name", "steamid", "team_name", "kast"]],
            on=["name", "steamid", "team_name"],
            how="left",
        )
        .merge(
            adr_df[["name", "steamid", "team_name", "adr"]],
            on=["name", "steamid", "team_name"],
        )
        .merge(
            impact_df[["name", "steamid", "team_name", "impact"]],
            on=["name", "steamid", "team_name"],
        )
        .merge(kills, on=["name", "steamid", "team_name"])
        .merge(deaths, on=["name", "steamid", "team_name"])
    )
    rating_df["rating"] = (
        0.0073 * rating_df["kast"]
        + 0.3591 * (rating_df["kills"] / rating_df["n_rounds"])
        - 0.5329 * (rating_df["deaths"] / rating_df["n_rounds"])
        + 0.2372 * rating_df["impact"]
        + 0.0032 * rating_df["adr"]
        + 0.1587
    )

    rating_df["kdr"] = (rating_df["kills"] / rating_df["deaths"])

    return rating_df

def extract_and_delete_zip(zip_path, extract_to = os.path.abspath(os.path.join('.', 'DOWNLOADED_DIR'))):
    # List to store the names of the files inside the ZIP
    extracted_files = []
    zip_path = os.path.join(extract_to, zip_path)
    # Extract the ZIP file
    with rarfile.RarFile(zip_path, 'r') as zip_ref:
        # Get the list of file names in the ZIP
        extracted_files = zip_ref.namelist()
        
        # Extract all the files to the specified directory
        zip_ref.extractall(extract_to)
    
    # Delete the ZIP file
    os.remove(zip_path)
    
    return extracted_files

def create_rounds_df(dem: Demo, file_src):
    dem.rounds["match_src"] = file_src.file_id
    side_clan_map = (
        dem.ticks[['round', 'team_name', 'team_clan_name']]
        .dropna()
        .drop_duplicates()
    )
    side_clan_map['winner'] = side_clan_map['team_name'].replace({'TERRORIST': 'T', 'CT': 'CT'})
    side_clan_map = side_clan_map.rename(columns={'team_clan_name': 'winner_clan_name'}).drop(['team_name'], axis = 1)

    rounds_df = pd.merge(dem.rounds,side_clan_map,on=['round', 'winner'], how='left', validate='one_to_one')

    equipment_value_at_freeze_end = []

    for _, round_info in dem.rounds.iterrows():
        round_num = round_info['round']
        freeze_end = round_info['freeze_end']
        
        # Get all the ticks for the current round from dem.ticks
        round_ticks = dem.ticks[dem.ticks['round'] == round_num]
        
        # Find the tick closest to freeze_end
        closest_tick_idx = (round_ticks['tick'] - freeze_end).abs().idxmin()
        closest_tick = round_ticks.loc[closest_tick_idx]
        
        # Aggregate the equipment value for each team (sum for all 5 players)
        # Group by team_clan_name and sum the current_equipment_value
        round_team_ticks = round_ticks[round_ticks['tick'] == closest_tick['tick']]
        team_equipment_value = round_team_ticks.groupby('team_name')['current_equip_value'].sum().reset_index()

        # Append the aggregated values and buy_type for each team
        for _, team_data in team_equipment_value.iterrows():
            equipment_value_at_freeze_end.append({
                'round': round_num,
                'team_name': team_data['team_name'],
                'current_equipment_value': team_data['current_equip_value']
            })

    # Convert the list to a DataFrame
    equipment_value_df = pd.DataFrame(equipment_value_at_freeze_end)

    def categorize_buy_type(equipment_value):
        if equipment_value >= 20000:
            return "Full Buy"
        elif equipment_value >= 10000:
            return "Semi Buy"
        elif equipment_value >= 5000:
            return "Semi Eco"
        else:
            return "Full Eco"

    # Apply categorization
    equipment_value_df['buy_type'] = equipment_value_df['current_equipment_value'].apply(categorize_buy_type)
    equipment_value_df['team_name'] = equipment_value_df['team_name'].replace("TERRORIST", "T")
    # Filter the buy-type DataFrame for T and CT teams
    t_buy_type_df = equipment_value_df[equipment_value_df['team_name'] == 'T']
    ct_buy_type_df = equipment_value_df[equipment_value_df['team_name'] == 'CT']

    # Rename the 'buy_type' column to t_buytype and ct_buytype
    t_buy_type_df = t_buy_type_df.rename(columns={'buy_type': 't_buytype', 'current_equipment_value': 't_equipment_value'})
    ct_buy_type_df = ct_buy_type_df.rename(columns={'buy_type': 'ct_buytype','current_equipment_value': 'ct_equipment_value'})

    # Merge the T and CT buy types into the dem.rounds DataFrame
    rounds_df = rounds_df.merge(t_buy_type_df[['round', 't_buytype', 't_equipment_value']], on='round', how='left', validate='1:1')
    rounds_df = rounds_df.merge(ct_buy_type_df[['round', 'ct_buytype', 'ct_equipment_value']], on='round', how='left', validate='1:1')

    return rounds_df

def add_source(file_src):
    #st.write(file_src)
    #st.write(f"awpy version: {importlib.metadata.version('awpy')}")

    if file_src.file_id in st.session_state.dem_list["file_id"].unique():
        st.write(f"Already parsed {file_src.name}, skipping parsing")
        return

    with tempfile.NamedTemporaryFile() as f:
        f.write(file_src.read())
        f.flush()

        dem = Demo(f.name, ticks=True)

    dem.header["match_src"] = file_src.file_id
    st.session_state.data_dict["header"].append(dem.header)

    rounds_df = create_rounds_df(dem, file_src)
    st.dataframe(rounds_df)
    st.session_state.data_dict["rounds"] = pd.concat([st.session_state.data_dict["rounds"], rounds_df]).reset_index(drop=True)

    dem.grenades["match_src"] = file_src.file_id
    grenades_df = dem.grenades.dropna(subset='thrower').merge(dem.ticks[['name', 'round', 'team_name']].drop_duplicates().rename(columns={'name': 'thrower'}),on=['thrower', 'round'], how = 'left', validate='many_to_one')
    st.session_state.data_dict["grenades"] = pd.concat([st.session_state.data_dict["grenades"], grenades_df]).reset_index(drop=True)

    dem.kills["match_src"] = file_src.file_id
    st.session_state.data_dict["kills"] = pd.concat([st.session_state.data_dict["kills"], calculate_trades(dem.kills)]).reset_index(drop=True)

    dem.damages["match_src"] = file_src.file_id
    st.session_state.data_dict["damages"] = pd.concat([st.session_state.data_dict["damages"], dem.damages]).reset_index(drop=True)

    dem.bomb["match_src"] = file_src.file_id
    st.session_state.data_dict["bomb"] = pd.concat([st.session_state.data_dict["bomb"], dem.bomb]).reset_index(drop=True)

    dem.smokes["match_src"] = file_src.file_id
    st.session_state.data_dict["smokes"] = pd.concat([st.session_state.data_dict["smokes"], dem.smokes]).reset_index(drop=True)

    dem.infernos["match_src"] = file_src.file_id
    st.session_state.data_dict["infernos"] = pd.concat([st.session_state.data_dict["infernos"], dem.infernos]).reset_index(drop=True)

    dem.weapon_fires["match_src"] = file_src.file_id
    st.session_state.data_dict["weapon_fires"] = pd.concat([st.session_state.data_dict["weapon_fires"], dem.weapon_fires]).reset_index(drop=True)

    st.session_state.dem_upload_count += 1
    dem.ticks["match_src"] = file_src.file_id
    st.session_state.data_dict["ticks"] = pd.concat([st.session_state.data_dict["ticks"], dem.ticks]).reset_index(drop=True)

    rating_table = rating2(dem)
    rating_table["match_src"] = file_src.file_id
    rating_table["map_name"] = dem.header['map_name']
    st.write("itt")
    st.write(rating_table)
    st.session_state.stats_df = pd.concat([st.session_state.stats_df, rating_table]).reset_index(drop=True)
    st.write(st.session_state.stats_df)

    st.session_state.data_dict["new_rating"] = pd.concat([st.session_state.data_dict["new_rating"], func.calculate_ratings([file_src.file_id])]).reset_index(drop=True)

    new_data = {
    "map_text": [dem.header["map_name"]],
    #"map": [f"/resources/maps/{dem.header["map_name"]}.png"],
    "map": [f"./app/static/maps/{dem.header['map_name']}.png"],
    "team1": [sorted(list(set(list(dem.kills['victim_team_clan_name'].dropna().unique()) + list(dem.kills['assister_team_clan_name'].dropna().unique()))))[0]],
    "team2": [sorted(list(set(list(dem.kills['victim_team_clan_name'].dropna().unique()) + list(dem.kills['assister_team_clan_name'].dropna().unique()))))[1]],
    "score": [f"{dem.rounds.merge(dem.ticks[['round','team_name','team_clan_name']].drop_duplicates().replace({'TERRORIST': 'T'}), how='left', validate='one_to_one', left_on=['round', 'winner'], right_on=['round', 'team_name']).groupby('team_clan_name').size().reset_index().sort_values(by='team_clan_name', ascending = True).values[0][1]} - {dem.rounds.merge(dem.ticks[['round','team_name','team_clan_name']].drop_duplicates().replace({'TERRORIST': 'T'}), how='left', validate='one_to_one', left_on=['round', 'winner'], right_on=['round', 'team_name']).groupby('team_clan_name').size().reset_index().sort_values(by='team_clan_name', ascending = True).values[1][1]}"],
    "source": ["manual upload"],
    "match_page": ["----"],
    "file_id": [file_src.file_id],
    "include/exclude/delete": ["Include"]
}
    st.session_state.dem_list = pd.concat([st.session_state.dem_list,pd.DataFrame(new_data)], ignore_index = True)
    #st.write(new_data)
    #st.write(dem.header)

    newer_data = {
        "id": [file_src.file_id],
        "name": [new_data['team1'][0] + " - " + new_data['team2'][0] + " " + new_data["score"][0]],
        "name - id": [new_data['team1'][0] + " - " + new_data['team2'][0] + " " + new_data["score"][0]+ " - " + file_src.file_id]
    }

    st.session_state.dem_id_name = pd.concat([st.session_state.dem_id_name,pd.DataFrame(newer_data)], ignore_index = True)

def add_source_hltv(file_src, match_page):
    #st.write(file_src)
    #st.write(f"awpy version: {importlib.metadata.version('awpy')}")

    if file_src in st.session_state.dem_list["file_id"].unique():
        st.write(f"Already parsed {file_src.name}, skipping parsing")
        return

    files = extract_and_delete_zip(file_src)

    for file in files:

        dem = Demo(os.path.join(os.path.abspath(os.path.join('.', 'DOWNLOADED_DIR')), file), ticks=True)

        dem.header["match_src"] = f"{file_src}_{file}"
        st.session_state.data_dict["header"].append(dem.header)

        rounds_df = create_rounds_df(dem, file_src)
        st.dataframe(rounds_df)
        st.session_state.data_dict["rounds"] = pd.concat([st.session_state.data_dict["rounds"], rounds_df]).reset_index(drop=True)

        dem.grenades["match_src"] = f"{file_src}_{file}"
        grenades_df = dem.grenades.dropna(subset='thrower').merge(dem.ticks[['name', 'round', 'team_name']].drop_duplicates().rename(columns={'name': 'thrower'}),on=['thrower', 'round'], how = 'left', validate='many_to_one')
        st.session_state.data_dict["grenades"] = pd.concat([st.session_state.data_dict["grenades"], grenades_df]).reset_index(drop=True)

        dem.kills["match_src"] = f"{file_src}_{file}"
        st.session_state.data_dict["kills"] = pd.concat([st.session_state.data_dict["kills"], calculate_trades(dem.kills)]).reset_index(drop=True)

        dem.damages["match_src"] = f"{file_src}_{file}"
        st.session_state.data_dict["damages"] = pd.concat([st.session_state.data_dict["damages"], dem.damages]).reset_index(drop=True)

        dem.bomb["match_src"] = f"{file_src}_{file}"
        st.session_state.data_dict["bomb"] = pd.concat([st.session_state.data_dict["bomb"], dem.bomb]).reset_index(drop=True)

        dem.smokes["match_src"] = f"{file_src}_{file}"
        st.session_state.data_dict["smokes"] = pd.concat([st.session_state.data_dict["smokes"], dem.smokes]).reset_index(drop=True)

        dem.infernos["match_src"] = f"{file_src}_{file}"
        st.session_state.data_dict["infernos"] = pd.concat([st.session_state.data_dict["infernos"], dem.infernos]).reset_index(drop=True)

        dem.weapon_fires["match_src"] = f"{file_src}_{file}"
        st.session_state.data_dict["weapon_fires"] = pd.concat([st.session_state.data_dict["weapon_fires"], dem.weapon_fires]).reset_index(drop=True)

        st.session_state.dem_upload_count += 1
        dem.ticks["match_src"] = f"{file_src}_{file}"
        st.session_state.data_dict["ticks"] = pd.concat([st.session_state.data_dict["ticks"], dem.ticks]).reset_index(drop=True)

        rating_table = rating2(dem)
        rating_table["match_src"] = file_src.file_id
        rating_table["map_name"] = dem.header['map_name']
        st.session_state.stats_df = pd.concat([st.session_state.stats_df, rating_table]).reset_index(drop=True)
        st.session_state.data_dict["new_rating"] = pd.concat([st.session_state.data_dict["new_rating"], func.calculate_ratings([file_src.file_id])]).reset_index(drop=True)
        try:
            new_data = {
        "map_text": [dem.header["map_name"]],
        #"map": [f"/resources/maps/{dem.header["map_name"]}.png"],
        "map": [f"./app/static/maps/{dem.header['map_name']}.png"],
        "team1": [sorted(list(set(list(dem.kills['victim_clan'].dropna().unique()) + list(dem.kills['attacker_clan'].dropna().unique()))))[0]],
        "team2": [sorted(list(set(list(dem.kills['victim_clan'].dropna().unique()) + list(dem.kills['attacker_clan'].dropna().unique()))))[1]],
        "score": [f"{dem.rounds.merge(dem.ticks[['round','side','clan']].drop_duplicates().replace({'TERRORIST': 'T'}), how='left', validate='one_to_one', left_on=['round', 'winner'], right_on=['round', 'side']).groupby('clan').size().reset_index().sort_values(by='clan', ascending = True).values[0][1]} - {dem.rounds.merge(dem.ticks[['round','side','clan']].drop_duplicates().replace({'TERRORIST': 'T'}), how='left', validate='one_to_one', left_on=['round', 'winner'], right_on=['round', 'side']).groupby('clan').size().reset_index().sort_values(by='clan', ascending = True).values[1][1]}"],
        "source": ["HLTV upload"],
        "match_page": [match_page],
        "file_id": [f"{file_src}_{file}"],
        "include/exclude/delete": ["Include"]
    }
        except Exception as e:
            new_data = {
        "map_text": [dem.header["map_name"]],
        #"map": [f"/resources/maps/{dem.header["map_name"]}.png"],
        "map": [f"./app/static/maps/{dem.header['map_name']}.png"],
        "team1": [sorted(list(set(list(dem.kills['victim_clan'].dropna().unique()) + list(dem.kills['attacker_clan'].dropna().unique()))))[0]],
        "team2": [sorted(list(set(list(dem.kills['victim_clan'].dropna().unique()) + list(dem.kills['attacker_clan'].dropna().unique()))))[1]],
        "score": [f"Parse ERROR"],
        "source": ["HLTV upload"],
        "match_page": [match_page],
        "file_id": [f"{file_src}_{file}"],
        "include/exclude/delete": ["Include"]
    }
        finally:
            st.session_state.dem_list = pd.concat([st.session_state.dem_list,pd.DataFrame(new_data)], ignore_index = True)
            #st.write(new_data)
            #st.write(dem.header)
            os.remove(os.path.join(os.path.abspath(os.path.join('.', 'DOWNLOADED_DIR')), file))
            newer_data = {
                "id": [f"{file_src}_{file}"],
                "name": [new_data['team1'][0] + " - " + new_data['team2'][0] + " " + new_data["score"][0]],
                "name - id": [new_data['team1'][0] + " - " + new_data['team2'][0] + " " + new_data["score"][0]+ " - " + file_src.file_id]
            }

            st.session_state.dem_id_name = pd.concat([st.session_state.dem_id_name,pd.DataFrame(newer_data)], ignore_index = True)