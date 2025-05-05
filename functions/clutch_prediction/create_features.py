import streamlit as st
import pandas as pd
import numpy as np
from awpy import Demo
from tqdm import tqdm

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

def create_df_for_class(data_df: Demo):

    clutch_df = pd.DataFrame()


    name_team_dict = {item.split('€')[0]: item.split('€')[1] for item in set(data_df.ticks['name'].astype(str) +'€'+ data_df.ticks['team_clan_name'].astype(str))}
    team1, team2 = set(name_team_dict.values())
    max_round = data_df.rounds['round'].max()
    #match_list = [match_list[0]]
    
    #'enemy_rifle_rate': [],
    #for match in match_list:
    clutch_ticks = []
    clutch_df_temp = pd.DataFrame()

    data = {'match_name': [], 'map_name': [], 'enemy_score': [], 'team_score': [],
        'round_num': [], 'player_side': [], 'player_health': [], 'player_armor': [], 
        'player_equipment_value': [], 'player_defuse_kit': [], 'player_bomb': [], 
        'player_utility_smoke': [], 'player_utility_flash': [], 'player_utility_heg': [], 
        'player_utility_molly': [], 'bomb_planted': [], 'team_equipment_value': [], 
        'team_previous_round_won': [], 'enemy_health_total': [], 'enemy_health_1': [], 
        'enemy_health_2': [],'enemy_health_3': [],'enemy_health_4': [],'enemy_health_5': [],
        'enemy_armor_rate': [], 'enemy_equipment_value': [], 'enemy_defuse_kit': [], 
        'tick_num': [], 'clutch_team': [], 'clutch_won': [], 'alive_enemies': [], 'enemy_utility_smoke': [], 
        'enemy_utility_flash': [], 'enemy_utility_heg': [], 'enemy_utility_molly': []}


    for round in range(1,max_round+1):
        kill_ticks = data_df.kills[data_df.kills['round'] == round]['tick'].unique()

        for tick in kill_ticks:
            #print(team1)
            team1_alive = (data_df.ticks[(data_df.ticks['tick']==tick)&(data_df.ticks['team_clan_name']==team1)&(data_df.ticks['health']>0)]['name'].nunique())
            team2_alive = (data_df.ticks[(data_df.ticks['tick']==tick)&(data_df.ticks['team_clan_name']==team2)&(data_df.ticks['health']>0)]['name'].nunique())
            if team1_alive == 1:
                #clutch_ticks.append([match,round,tick,team1,team1==data_df.rounds[data_df.rounds['round']==round]['winner_clan_name'].values[0],team2_alive])
                clutch_player = data_df.ticks[(data_df.ticks['tick']==tick)&(data_df.ticks['team_clan_name']==team1)&(data_df.ticks['health'] > 0)]['name'].unique()[0]
                clutch_side = data_df.ticks[(data_df.ticks['round']==round)&(data_df.ticks['team_clan_name']==team1)]['team_name'].values[0]  
                clutch_team_score = data_df.rounds[(data_df.rounds['round'] < round) & (data_df.rounds['winner_clan_name'] == team1)].shape[0]
                enemy_team_score = round - clutch_team_score - 1
                
                enemy_health_list = list(data_df.ticks[(data_df.ticks['tick'] == tick)&(data_df.ticks['team_clan_name'] == team2)]['health'].sort_values(ascending=False))
                for i in range(len(enemy_health_list),5):
                    enemy_health_list.append(0)
                enemy_armor_list = list(data_df.ticks[(data_df.ticks['tick']==tick) & (data_df.ticks['team_clan_name']==team2)]['armor_value'])

                data['match_name'].append(data_df.path)
                data['player_side'].append(clutch_side)
                data['map_name'].append(st.session_state.dem_list[st.session_state.dem_list['file_id']==st.session_state.dem_id_name[st.session_state.dem_id_name['name - id'] == data_df.path]['id'].values[0]]['map_text'].values[0])
                data['enemy_score'].append(enemy_team_score)
                data['player_health'].append(data_df.ticks[(data_df.ticks['name']==clutch_player)&(data_df.ticks['tick']==tick)]['health'].values[0])
                data['player_armor'].append(True if data_df.ticks[(data_df.ticks['name']==clutch_player)&(data_df.ticks['tick']==tick)]['armor_value'].values[0]>0 else False)
                data['player_equipment_value'].append(data_df.ticks[(data_df.ticks['name']==clutch_player)&(data_df.ticks['tick']==tick)]['current_equip_value'].values[0])
                data['player_defuse_kit'].append(data_df.ticks[(data_df.ticks['name']==clutch_player)&(data_df.ticks['tick']==tick)]['has_defuser'].values[0])
                data['player_bomb'].append('C4' in data_df.ticks[(data_df.ticks['name']==clutch_player)&(data_df.ticks['tick']==tick)]['inventory'].values[0])
                data['player_utility_flash'].append(1 if 'Flashbang' in data_df.ticks[(data_df.ticks['name']==clutch_player)&(data_df.ticks['tick']==tick)]['inventory'].values[0] else 0)
                data['player_utility_smoke'].append(1 if 'Smoke Grenade' in data_df.ticks[(data_df.ticks['name']==clutch_player)&(data_df.ticks['tick']==tick)]['inventory'].values[0] else 0)
                data['player_utility_heg'].append(1 if 'High Explosive Grenade' in data_df.ticks[(data_df.ticks['name']==clutch_player)&(data_df.ticks['tick']==tick)]['inventory'].values[0] else 0)
                data['player_utility_molly'].append(1 if 'Molotov' in data_df.ticks[(data_df.ticks['name']==clutch_player)&(data_df.ticks['tick']==tick)]['inventory'].values[0] else 1 if 'Incendiary Grenade' in data_df.ticks[(data_df.ticks['name']==clutch_player)&(data_df.ticks['tick']==tick)]['inventory'].values[0] else 0)
                data['bomb_planted'].append(data_df.ticks[(data_df.ticks['name']==clutch_player)&(data_df.ticks['tick']==tick)]['is_bomb_planted'].values[0])
                data['team_equipment_value'].append(data_df.rounds[(data_df.rounds['round']==round)]['ct_equipment_value'].values[0] if clutch_side == 'CT' else data_df.rounds[(data_df.rounds['round']==round)]['t_equipment_value'].values[0])
                data['team_previous_round_won'].append(data_df.rounds[(data_df.rounds['round']==round-1)]['winner_clan_name'].values[0] == team1 if round>1 else 'N/A')
                data['team_score'].append(clutch_team_score)
                data['round_num'].append(round)
                data['tick_num'].append(tick)
                data['clutch_team'].append(team1)
                data['clutch_won'].append(team1==data_df.rounds[data_df.rounds['round']==round]['winner_clan_name'].values[0])
                data['alive_enemies'].append(team2_alive)
                #for i in range(len(enemy_health_list)):
                for i in range(5):
                    data[f'enemy_health_{i+1}'].append(enemy_health_list[i])
                data['enemy_health_total'].append(sum(enemy_health_list))
                data['enemy_armor_rate'].append(sum(1 for x in enemy_armor_list if x > 0) / team2_alive) if team2_alive !=0 else data['enemy_armor_rate'].append(0)
                data['enemy_equipment_value'].append(data_df.rounds[(data_df.rounds['round']==round)]['ct_equipment_value'].values[0] if clutch_side != 'CT' else data_df.rounds[(data_df.rounds['round']==round)]['t_equipment_value'].values[0])
                data['enemy_defuse_kit'].append(any(x for x in list(data_df.ticks[(data_df.ticks['tick']==tick) & (data_df.ticks['team_clan_name']==team2)& (data_df.ticks['health']>0)]['has_defuser'])))
                data['enemy_utility_flash'].append(1)#sum(data_df.ticks[(data_df.ticks['tick']==tick) & (data_df.ticks['team_clan_name']==team2)& (data_df.ticks['isAlive']==True)]['flashGrenades']))
                data['enemy_utility_heg'].append(1)#sum(data_df.ticks[(data_df.ticks['tick']==tick) & (data_df.ticks['team_clan_name']==team2)& (data_df.ticks['isAlive']==True)]['heGrenades']))
                data['enemy_utility_molly'].append(1)#sum(data_df.ticks[(data_df.ticks['tick']==tick) & (data_df.ticks['team_clan_name']==team2)& (data_df.ticks['isAlive']==True)]['fireGrenades']))
                data['enemy_utility_smoke'].append(1)#sum(data_df.ticks[(data_df.ticks['tick']==tick) & (data_df.ticks['team_clan_name']==team2)& (data_df.ticks['isAlive']==True)]['smokeGrenades']))

                break
            #print(team2)
            if team2_alive == 1:
                #clutch_ticks.append([match,round,tick,team2,team2==data_df.rounds[data_df.rounds['round']==round]['winner_clan_name'].values[0],team1_alive])
                clutch_player = data_df.ticks[(data_df.ticks['tick']==tick)&(data_df.ticks['team_clan_name']==team2)&(data_df.ticks['health']>0)]['name'].unique()[0]
                clutch_side = data_df.ticks[(data_df.ticks['round']==round)&(data_df.ticks['team_clan_name']==team2)]['team_name'].values[0]
                clutch_team_score = data_df.rounds[(data_df.rounds['round'] < round) & (data_df.rounds['winner_clan_name'] == team2)].shape[0]
                enemy_team_score = round - clutch_team_score - 1
                
                enemy_health_list = list(data_df.ticks[(data_df.ticks['tick'] == tick)&(data_df.ticks['team_clan_name'] == team1)]['health'].sort_values(ascending=False))
                for i in range(len(enemy_health_list),5):
                    enemy_health_list.append(0)
                enemy_armor_list = list(data_df.ticks[(data_df.ticks['tick']==tick) & (data_df.ticks['team_clan_name']==team1)]['armor_value'])

                data['match_name'].append(data_df.path)
                data['player_side'].append(clutch_side)                       
                data['map_name'].append(st.session_state.dem_list[st.session_state.dem_list['file_id']==st.session_state.dem_id_name[st.session_state.dem_id_name['name - id'] == data_df.path]['id'].values[0]]['map_text'].values[0])
                data['enemy_score'].append(enemy_team_score)
                data['player_health'].append(data_df.ticks[(data_df.ticks['name']==clutch_player)&(data_df.ticks['tick']==tick)]['health'].values[0])
                data['player_armor'].append(True if data_df.ticks[(data_df.ticks['name']==clutch_player)&(data_df.ticks['tick']==tick)]['armor_value'].values[0]>0 else False)
                data['player_equipment_value'].append(data_df.ticks[(data_df.ticks['name']==clutch_player)&(data_df.ticks['tick']==tick)]['current_equip_value'].values[0])
                data['player_defuse_kit'].append(data_df.ticks[(data_df.ticks['name']==clutch_player)&(data_df.ticks['tick']==tick)]['has_defuser'].values[0])
                data['player_bomb'].append('C4' in data_df.ticks[(data_df.ticks['name']==clutch_player)&(data_df.ticks['tick']==tick)]['inventory'].values[0])
                data['player_utility_flash'].append(1 if 'Flashbang' in data_df.ticks[(data_df.ticks['name']==clutch_player)&(data_df.ticks['tick']==tick)]['inventory'].values[0] else 0)
                data['player_utility_smoke'].append(1 if 'Smoke Grenade' in data_df.ticks[(data_df.ticks['name']==clutch_player)&(data_df.ticks['tick']==tick)]['inventory'].values[0] else 0)
                data['player_utility_heg'].append(1 if 'High Explosive Grenade' in data_df.ticks[(data_df.ticks['name']==clutch_player)&(data_df.ticks['tick']==tick)]['inventory'].values[0] else 0)
                data['player_utility_molly'].append(1 if 'Molotov' in data_df.ticks[(data_df.ticks['name']==clutch_player)&(data_df.ticks['tick']==tick)]['inventory'].values[0] else 1 if 'Incendiary Grenade' in data_df.ticks[(data_df.ticks['name']==clutch_player)&(data_df.ticks['tick']==tick)]['inventory'].values[0] else 0)
                data['bomb_planted'].append(data_df.ticks[(data_df.ticks['name']==clutch_player)&(data_df.ticks['tick']==tick)]['is_bomb_planted'].values[0])
                data['team_equipment_value'].append(data_df.rounds[(data_df.rounds['round']==round)]['ct_equipment_value'].values[0] if clutch_side == 'CT' else data_df.rounds[(data_df.rounds['round']==round)]['t_equipment_value'].values[0])
                data['team_previous_round_won'].append(data_df.rounds[(data_df.rounds['round']==round-1)]['winner_clan_name'].values[0] == team2 if round>1 else 'N/A')
                data['team_score'].append(clutch_team_score)
                data['round_num'].append(round)
                data['tick_num'].append(tick)
                data['clutch_team'].append(team2)
                data['clutch_won'].append(team2==data_df.rounds[data_df.rounds['round']==round]['winner_clan_name'].values[0])
                data['alive_enemies'].append(team1_alive)
                #for i in range(len(enemy_health_list)):
                for i in range(5):
                    data[f'enemy_health_{i+1}'].append(enemy_health_list[i])
                data['enemy_health_total'].append(sum(enemy_health_list))
                data['enemy_armor_rate'].append(sum(1 for x in enemy_armor_list if x > 0) / team1_alive) if team1_alive !=0 else data['enemy_armor_rate'].append(0)
                data['enemy_equipment_value'].append(data_df.rounds[(data_df.rounds['round']==round)]['ct_equipment_value'].values[0] if clutch_side != 'CT' else data_df.rounds[(data_df.rounds['round']==round)]['t_equipment_value'].values[0])
                data['enemy_defuse_kit'].append(any(x for x in list(data_df.ticks[(data_df.ticks['tick']==tick) & (data_df.ticks['team_clan_name']==team1)& (data_df.ticks['health']>0)]['has_defuser'])))
                data['enemy_utility_flash'].append(1)#sum(data_df.ticks[(data_df.ticks['tick']==tick) & (data_df.ticks['team_clan_name']==team1)& (data_df.ticks['isAlive']==True)]['flashGrenades']))
                data['enemy_utility_heg'].append(1)#sum(data_df.ticks[(data_df.ticks['tick']==tick) & (data_df.ticks['team_clan_name']==team1)& (data_df.ticks['isAlive']==True)]['heGrenades']))
                data['enemy_utility_molly'].append(1)#sum(data_df.ticks[(data_df.ticks['tick']==tick) & (data_df.ticks['team_clan_name']==team1)& (data_df.ticks['isAlive']==True)]['fireGrenades']))
                data['enemy_utility_smoke'].append(1)#sum(data_df.ticks[(data_df.ticks['tick']==tick) & (data_df.ticks['team_clan_name']==team1)& (data_df.ticks['isAlive']==True)]['smokeGrenades']))

                break
    #clutch_df_temp = pd.DataFrame(clutch_ticks)
    #print(clutch_df_temp)
    #clutch_df = pd.concat([clutch_df, clutch_df_temp])

    # TEMPORARY UNTIL NOT ALL COLUMNS ARE CALCULATED
    # Loop through the keys
    for key in data:
        if len(data[key]) == 0:
            data[key] = [''] * len(data['match_name'])#22#1646
    clutch_df2 = pd.DataFrame(data)
    return clutch_df2


def create_feature_table_class(files: list):
    result_df = pd.DataFrame(columns=[
        'match_name', 'map_name', 'enemy_score', 'team_score',
            'round_num', 'player_side', 'player_health', 'player_armor', 
            'player_equipment_value', 'player_defuse_kit', 'player_bomb', 
            'player_utility_smoke', 'player_utility_flash', 'player_utility_heg', 
            'player_utility_molly', 'bomb_planted', 'team_equipment_value', 
            'team_previous_round_won', 'enemy_health_total', 'enemy_health_1', 
            'enemy_health_2','enemy_health_3','enemy_health_4','enemy_health_5',
            'enemy_armor_rate', 'enemy_equipment_value', 'enemy_defuse_kit', 
            'tick_num', 'clutch_team', 'clutch_won', 'alive_enemies', 'enemy_utility_smoke', 
            'enemy_utility_flash', 'enemy_utility_heg', 'enemy_utility_molly'
    ])
    result_df = pd.DataFrame()
    error_count_all = 0

    for file in tqdm(files):
        dem = DemoFromDataBase(file)
        current_df = create_df_for_class(dem)
        result_df = pd.concat([result_df, current_df], ignore_index = True)

    st.write(f"error num: {error_count_all}")
    return result_df
    # result_df.to_csv('raw_data_new.csv', sep = '|')