from awpy import Demo
import pandas as pd
from tqdm import tqdm
import streamlit as st

class DemoFromDataBase():

    def __init__(self, match_id):

        self.kills = st.session_state.data_dict['kills'][st.session_state.data_dict['kills']['match_src']==match_id]
        self.damages = st.session_state.data_dict['damages'][st.session_state.data_dict['damages']['match_src']==match_id]
        self.bomb = st.session_state.data_dict['bomb'][st.session_state.data_dict['bomb']['match_src']==match_id]
        self.smokes = st.session_state.data_dict['smokes'][st.session_state.data_dict['smokes']['match_src']==match_id]
        self.infernos = st.session_state.data_dict['infernos'][st.session_state.data_dict['infernos']['match_src']==match_id]
        self.weapon_fires = st.session_state.data_dict['weapon_fires'][st.session_state.data_dict['weapon_fires']['match_src']==match_id]
        self.rounds = st.session_state.data_dict['rounds'][st.session_state.data_dict['rounds']['match_src']==match_id]
        self.grenades = st.session_state.data_dict['grenades'][st.session_state.data_dict['grenades']['match_src']==match_id]
        self.ticks = st.session_state.data_dict['ticks'][st.session_state.data_dict['ticks']['match_src']==match_id]
        self.path = st.session_state.dem_id_name[st.session_state.dem_id_name['id'] == match_id]['name - id'].values[0]

def get_bomb_carried_for_stat(round_ticks, player):
    # Check if 'C4' is in the inventory column across all filtered ticks
    bomb_carriage_ticks = round_ticks[round_ticks['name']==player]['inventory'].apply(lambda inv: 'C4' in inv)
    
    # Count how many ticks the bomb is carried
    tick_counter_for_bomb_carriage = bomb_carriage_ticks.sum()
    
    round_len = round_ticks['tick'].max() - round_ticks['tick'].min()
    # Return the proportion of time the bomb was carried during the round
    return tick_counter_for_bomb_carriage / round_len

def get_awp_used_in_round(round_ticks, player):  
    # Check if 'C4' is in the inventory column across all filtered ticks
    awp_carried_ticks = round_ticks[round_ticks['name']==player]['inventory'].apply(lambda inv: 'AWP' in inv)

    return awp_carried_ticks.sum() > 0

def get_distance_travelled_stat(round_ticks, player):
    import numpy as np
    
    # Sort the ticks by time to calculate distance between consecutive positions
    player_ticks = round_ticks[round_ticks['name']==player].sort_values('tick')
    
    # Calculate the Euclidean distance between consecutive ticks
    distances = np.sqrt(
        np.diff(player_ticks['X'])**2 +
        np.diff(player_ticks['Y'])**2 +
        np.diff(player_ticks['Z'])**2
    )
    
    # Sum the distances to get the total distance traveled
    total_distance_traveled = distances.sum()
    
    return total_distance_traveled

def get_last_alive_flag(round_ticks, player, name_team_dict):
    last_alive_tick_for_player = round_ticks[(round_ticks['name']==player)&(round_ticks['health']>0)].sort_values('tick', ascending=False)['tick'].values[0]
    alive_teammates_last_alive_tick = round_ticks[(round_ticks['team_clan_name']==name_team_dict[player])&(round_ticks['name']!=player)&(round_ticks['health']>0)&(round_ticks['tick']==last_alive_tick_for_player)]
    return len(alive_teammates_last_alive_tick) == 0

def get_team_equipment_value(rounds, round_ticks, round_num, player, name_team_dict):
    round_data = rounds[rounds['round'] == round_num]
    start = round_data['freeze_end'].values[0]

    closest_tick_idx = (round_ticks['tick'] - start).abs().idxmin()
    closest_tick = round_ticks.loc[closest_tick_idx]['tick']

    return round_ticks[(round_ticks['tick'] == closest_tick)&(round_ticks['team_clan_name'] == name_team_dict[player])]['current_equip_value'].sum()

def get_enemy_equipment_value(rounds, round_ticks, round_num, player, name_team_dict):
    round_data = rounds[rounds['round'] == round_num]
    start = round_data['freeze_end'].values[0]

    closest_tick_idx = (round_ticks['tick'] - start).abs().idxmin()
    closest_tick = round_ticks.loc[closest_tick_idx]['tick']

    return round_ticks[(round_ticks['tick'] == closest_tick)&(round_ticks['team_clan_name'] != name_team_dict[player])]['current_equip_value'].sum()

def create_df_for_cluster(dem: Demo):
    import pandas as pd
    from tqdm import tqdm
    
    #dem.ticks['name'] = dem.ticks['name']
    #dem.ticks['team_clan_name'] = dem.ticks['team_clan_name']
    name_team_dict = {item.split('€')[0]: item.split('€')[1] for item in set(dem.ticks['name'].astype(str) +'€'+ dem.ticks['team_clan_name'].astype(str))}
    data = {
    'name': [], 'team_name': [], 'team_side': [], 'team_equipment_value': [],
    'enemy_equipment_value': [], 'match_name': [], 'round_num': [], 
    'kills_in_round': [], 'deaths_in_round': [], 'dmg_in_round': [], 
    'dmg_taken_in_round': [], 'dmg_in_round_util': [], 'entry_kill': [], 
    'entry_damages': [], 'round_survived': [], 'bomb_carried_ratio': [], 
    'distance_travelled': [], 'attacking_util_threw': [], 'supporting_util_threw': [], 
    'last_alive_flag': [], 'hs_kill_count': [], 'kill_count': [], 
    'kill_count_team': [], 'kill_participate_ratio': [], 'assist_count': [], 
    'assist_participate_ratio': [], 'awp_used_flag': [], 'engagement_count': [],
    'round_won': [], 'round_time': [], 'alive_time': []
}
    round_count = dem.rounds['round'].max()

    error_count = 0

    for round_num in (range(1, round_count + 1)):
        # rounds_to_exclude = [1, 13] have to exclude rounds in later phase
        rounds_to_exclude = []
        if round_num in rounds_to_exclude:
            continue
        round_ticks = dem.ticks[dem.ticks['round'] == round_num]
        round_kills = dem.kills[dem.kills['round'] == round_num]
        round_damages = dem.damages[dem.damages['round'] == round_num]
        round_grenades = dem.grenades[dem.grenades['round'] == round_num]
        for player in name_team_dict.keys():
            try:
                # print(f"team: {name_team_dict[player]}, player: {player}, round: {round_num}")
                not_alive_ticks = round_ticks[(round_ticks['name']==player) & (round_ticks['health']==0)]
                team_side = round_ticks[(round_ticks['name']==player)]['team_name'].values[0].replace('TERRORIST', 'T')
                team_name = name_team_dict[player]
                team_equipment_value = get_team_equipment_value(dem.rounds,round_ticks,round_num,player,name_team_dict)
                enemy_equipment_value = get_enemy_equipment_value(dem.rounds,round_ticks,round_num,player,name_team_dict)
                match_name = str(dem.path)
                kills_in_round = len(round_kills[(round_kills['attacker_name'] == player)])
                deaths_in_round = len(round_kills[(round_kills['victim_name'] == player)])
                dmg_in_round = round_damages[(round_damages['attacker_name'] == player)]['dmg_health_real'].sum()
                dmg_taken_in_round = round_damages[(round_damages['victim_name'] == player)]['dmg_health_real'].sum()
                dmg_in_round_util = round_damages[(round_damages['attacker_name'] == player) & (round_damages['weapon'].isin(['inferno', 'hegrenade']))]['dmg_health_real'].sum()
                entry_kill = player == round_kills.sort_values('tick', ascending = True)['attacker_name'].values[0] if len(round_kills) > 0 else False
                entry_damages = player in round_damages.sort_values('tick', ascending = True)['attacker_name'].values[:10] if len(round_damages) > 0 else False
                round_survived = 1 - deaths_in_round
                bomb_carried_ratio = get_bomb_carried_for_stat(round_ticks,player)
                distance_travelled = get_distance_travelled_stat(round_ticks,player)
                attacking_util_threw = len(round_grenades[(round_grenades['thrower'] == player) & (round_grenades['grenade_type'].isin(['molotov','he_grenade','incendiary_grenade']))].drop_duplicates(subset = ['entity_id']))
                supporting_util_threw = len(round_grenades[(round_grenades['thrower'] == player) & (round_grenades['grenade_type'].isin(['smoke','flashbang']))].drop_duplicates(subset = ['entity_id']))
                last_alive_flag = get_last_alive_flag(round_ticks,player,name_team_dict)
                hs_kill_count = len(round_kills[(round_kills['attacker_name']==player)&(round_kills['headshot'])])
                kill_count = len(round_kills[(round_kills['attacker_name']==player)])
                kill_count_team = len(round_kills[(round_kills['attacker_team_clan_name']==name_team_dict[player])])
                kill_participate_ratio = kill_count / kill_count_team if kill_count_team != 0 else 0
                assist_count = len(round_kills[(round_kills['assister_name']==player)])
                assist_participate_ratio = assist_count / kill_count_team if kill_count_team != 0 else 0
                awp_used_flag = get_awp_used_in_round(round_ticks,player)
                engagement_count = len(round_damages[((round_damages['attacker_name']==player)|(round_damages['victim_name']==player))])
                round_won = dem.rounds[dem.rounds['round']==round_num]['winner'].values[0] == team_side
                round_time = (dem.rounds[dem.rounds['round']==round_num]['official_end'].values[0] - dem.rounds[dem.rounds['round']==round_num]['start'].values[0]) / 64
                alive_time = (not_alive_ticks['tick'].min() - dem.rounds[dem.rounds['round']==round_num]['start'].values[0]) / 64 if len(not_alive_ticks) > 0 else round_time
                

                data['name'].append(player)
                data['team_name'].append(team_name)
                data['team_side'].append(team_side)
                data['team_equipment_value'].append(team_equipment_value)
                data['enemy_equipment_value'].append(enemy_equipment_value)
                data['match_name'].append(match_name)
                data['round_num'].append(round_num)
                data['kills_in_round'].append(kills_in_round)
                data['deaths_in_round'].append(deaths_in_round)
                data['dmg_in_round'].append(dmg_in_round)
                data['dmg_taken_in_round'].append(dmg_taken_in_round)
                data['dmg_in_round_util'].append(dmg_in_round_util)
                data['entry_kill'].append(entry_kill)
                data['entry_damages'].append(entry_damages)
                data['round_survived'].append(round_survived)
                data['bomb_carried_ratio'].append(bomb_carried_ratio)
                data['distance_travelled'].append(distance_travelled)
                data['attacking_util_threw'].append(attacking_util_threw)
                data['supporting_util_threw'].append(supporting_util_threw)
                data['last_alive_flag'].append(last_alive_flag)
                data['hs_kill_count'].append(hs_kill_count)
                data['kill_count'].append(kill_count)
                data['kill_count_team'].append(kill_count_team)
                data['kill_participate_ratio'].append(kill_participate_ratio)
                data['assist_count'].append(assist_count)
                data['assist_participate_ratio'].append(assist_participate_ratio)
                data['awp_used_flag'].append(awp_used_flag)
                data['engagement_count'].append(engagement_count)
                data['round_won'].append(round_won)
                data['round_time'].append(round_time)
                data['alive_time'].append(alive_time)
                # result_df = pd.concat([result_df, temp_df], ignore_index=True)
            except Exception as e:
                error_count += 1
                print(str(e))

    result_df = pd.DataFrame(data)

    return result_df, error_count

def create_feature_table(files: list):
    result_df = pd.DataFrame(columns=[
        'name', 'team_name', 'team_side', 'team_equipment_value', 'enemy_equipment_value', 'match_name', 'round_num',
        'kills_in_round', 'deaths_in_round', 'dmg_in_round', 'dmg_taken_in_round', 'dmg_in_round_util',
        'entry_kill', 'entry_damages', 'round_survived', 'bomb_carried_ratio', 'distance_travelled',
        'attacking_util_threw', 'supporting_util_threw', 'last_alive_flag', 'hs_kill_count',
        'kill_count', 'kill_count_team', 'kill_participate_ratio', 'assist_count', 
        'assist_participate_ratio', 'awp_used_flag', 'engagement_count'
    ])
    result_df = pd.DataFrame()
    error_count_all = 0

    for file in tqdm(files):
        dem = DemoFromDataBase(file)
        current_df, error_num = create_df_for_cluster(dem)
        result_df = pd.concat([result_df, current_df], ignore_index = True)
        error_count_all += error_num

    st.write(f"error num: {error_count_all}")
    return result_df
    # result_df.to_csv('raw_data_new.csv', sep = '|')