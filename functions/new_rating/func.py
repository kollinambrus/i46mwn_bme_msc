import os
import glob
import pandas as pd
from .helper import rating_weights
import streamlit as st

def get_folder_names(path):
    folder_names = [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]
    return folder_names

def read_match(match_list):
    data_df={}

    data_df['rounds'] = st.session_state.data_dict['rounds'][st.session_state.data_dict['rounds']['match_src'] == match_list]
    data_df['grenades'] = st.session_state.data_dict['grenades'][st.session_state.data_dict['grenades']['match_src'] == match_list]
    data_df['kills'] = st.session_state.data_dict['kills'][st.session_state.data_dict['kills']['match_src'] == match_list]
    data_df['damages'] = st.session_state.data_dict['damages'][st.session_state.data_dict['damages']['match_src'] == match_list]
    data_df['bomb'] = st.session_state.data_dict['bomb'][st.session_state.data_dict['bomb']['match_src'] == match_list]
    data_df['smokes'] = st.session_state.data_dict['smokes'][st.session_state.data_dict['smokes']['match_src'] == match_list]
    data_df['infernos'] = st.session_state.data_dict['infernos'][st.session_state.data_dict['infernos']['match_src'] == match_list]
    data_df['weapon_fires'] = st.session_state.data_dict['weapon_fires'][st.session_state.data_dict['weapon_fires']['match_src'] == match_list]
    data_df['ticks'] = st.session_state.data_dict['ticks'][st.session_state.data_dict['ticks']['match_src'] == match_list]
    return data_df

def create_team_name_dict(data_df):
    name_team_dict = (
    data_df['ticks'][['name', 'team_clan_name']]
    .drop_duplicates()
    .dropna()
    .set_index('name')['team_clan_name']
    .to_dict()
)

    return name_team_dict

def calculate_ratings(match_list: list):
    # match_list = get_folder_names(folder)
    rating_df=pd.DataFrame(columns=["match_src","RoundNum","Player","PositiveRating","NegativeRating","Rating"])
    for match in match_list:
        print(fr"reading match: {match}")
        data_df=read_match(match)
        name_team_dict=create_team_name_dict(data_df)
        

        #for player in name_team_dict.keys():
            #rating_df=pd.concat([rating_df,func.calculate_ratings_for_match(match,data_df,name_team_dict,player)])

        #rating_df=pd.DataFrame(columns=["match_src","round","Player","PositiveRating","NegativeRating","Rating"])
        for player in name_team_dict.keys():
            for round_num in range(1,data_df['rounds']['round'].max()+1):
                #round_num=5
                #STARTING POSITION (ROLE) SHOULD BE CONSIDERED INTO (INITIAL?) RATING: FOR EXAMPLE IF THE PLAYER HAS AN AWP WEAPON, OR IN A PISTOL HE HAS A DEFUSE KIT, HIS DEATH SHOULD IMPACT THE RATING MORE NEGATIVELY
                #PISTOL RATING SHOULD BE CALCULATED DIFFERENTLY#
                first=True

                initial_rating=0

                first_round=data_df['rounds'][data_df['rounds']['round']==round_num]
                start_tick=first_round['start'].values[0]
                end_tick=first_round['official_end'].values[0]
                end_tick = (data_df['ticks']['tick'] - end_tick).abs().idxmin()
                end_tick = data_df['ticks'].loc[end_tick]['tick']

                #IF ROUND END REASON IS TERRORISTS WIN, LAST DEATHS ON LOSING SIDE SHOULD BE MORE PUNISHED, BECAUSE SAVING THE WEAPONS WOULD HAVE BEEN MORE IMPORTANT, BUT ON THE WINNING SIDE IT SHOULD NOT BE THAT REWARDED
                #IF ROUND END REASON IS BOMBEXPLODED, FIRST DEATHS ON LOSING SIDE SHOULD BE MORE PUNISHED, BECAUSE LOSING THE EARLY DUELS LED TO LOSING THE ROUND, AND FIRST KILLS SHOULD BE MORE REWARDED
                #IF ROUND END REASON IS BOMBDEFUSED, LAST DEATHS ON LOSING SIDE SHOULD BE MORE PUNISHED, AND LAST KILLS ON WINNING SIDE SHOULD BE MORE REWARDED
                #IF ROUND END REASON IS CT WIN, FIRST KILLS SHOULD BE MORE REWARDED ON THE WINNING SIDE, AND LAST DEATHS ON THE TERRORIST SIDE SHOULD BE MORE PUNISHED
                #RATING SHOULD NOT BE BASED ON KILLS/DEATHS, IT SHOULD TAKE ROUND WINNING INTO CONSIDERATION (AN ACE ON A LOST ROUND SHOULD NOT HAVE A GOOD RATING, DESPITE MAKING A BIG ECONOMICAL DAMAGE ON THE ENEMY TEAM, THE MOST IMPORTANT THING IS TO WIN THE ROUND)
                round_end_reason=first_round['reason'].values[0]

                player_frames=data_df['ticks'][(data_df['ticks']['name']==player) & (data_df['ticks']['round']==round_num)]
                player_damages=data_df['damages'][(data_df['damages']['attacker_name']==player) & (data_df['damages']['round']==round_num)]
                player_kills=data_df['kills'][(data_df['kills']['attacker_name']==player) & (data_df['kills']['round']==round_num)]
                dead_on_round_end=list(data_df['ticks'][(data_df['ticks']['tick']==end_tick) & (data_df['ticks']['health']==0)]['name'])
                player_dmg_in_round=player_damages['dmg_health_real'].sum()
                player_damaged_players=player_damages['victim_name'].unique()
                player_damaged_players_killed=player_kills['victim_name'].unique()
                #player_damaged_players_helped = list(set(player_damaged_players) & set(dead_on_round_end))
                #player_damaged_players_helped = list(set(player_damaged_players_helped) - set(player_damaged_players_killed))
                help_damage=pd.DataFrame(columns=['RoundProgress','Victim','Damage','TimeElapsed','KillNumber','IsTrade','RoundEndReason','PlayerTeamWon','KilledHelpedAliveFlag','PlayerWeapon','VictimWeapon','PlayerTeamEconomy','VictimTeamEconomy','AliveTeammates'])
                for helped_victim in player_damaged_players:
                    if helped_victim in dead_on_round_end:
                        kill_number = data_df['kills'][(data_df['kills']['round'] == round_num) & (data_df['kills']['victim_team_clan_name'] == name_team_dict[helped_victim])].reset_index(drop=True)
                        kill_number = kill_number[kill_number['victim_name'] == helped_victim].index[0]+1

                        killed_at = 0#pd.to_datetime(data_df['kills'][(data_df['kills']['round'] == round_num) & (data_df['kills']['victim_name'] == helped_victim)]['clock'], format='%M:%S')
                        last_help_at = 0#pd.to_datetime(data_df['damages'][(data_df['damages']['round'] == round_num) & (data_df['damages']['victim_name'] == helped_victim)& (data_df['damages']['attacker_name'] == player)].tail(1)['clock'], format='%M:%S')
                        time_difference_seconds = 0#(last_help_at.iloc[0] - killed_at.iloc[0]).total_seconds()
                    else:
                        kill_number=0
                        time_difference_seconds=0
                    last_tick_dmg=data_df['damages'][(data_df['damages']['round'] == round_num) & (data_df['damages']['victim_name'] == helped_victim)& (data_df['damages']['attacker_name'] == player)].tail(1)['tick'].unique()[0] 
                    last_tick_dmg_frame = (data_df['ticks']['tick'] - last_tick_dmg).abs().idxmin()
                    last_tick_dmg_frame = data_df['ticks'].loc[last_tick_dmg_frame]['tick']


                    player_weapon=list(data_df['damages'][(data_df['damages']['round']==round_num)&(data_df['damages']['attacker_name']==player)&(data_df['damages']['victim_name']==helped_victim)]['weapon'].unique())
                    #print(fr"last tick dmg: {last_tick_dmg}, helped victim: {helped_victim}")
                    victim_weapon=['AK-47'] # not used...data_df['ticks'][(data_df['ticks']['tick']==last_tick_dmg_frame)&(data_df['ticks']['name']==helped_victim)]['inventory'].values[0][-1]

                    player_team_economy="full"
                    victim_team_economy="eco"

                    # new below clock_time=data_df['damages'][data_df['damages']['tick']==last_tick_dmg]['seconds'].values[0]/((data_df['rounds'][data_df['rounds']['round']==round_num]['endTick'].values[0]-data_df['rounds'][data_df['rounds']['round']==round_num]['freezeTimeEndTick'].values[0])/128)
                    clock_time= (last_tick_dmg - data_df['rounds'][data_df['rounds']['round']==round_num]['freeze_end'].values[0]) / (data_df['rounds'][data_df['rounds']['round']==round_num]['official_end'].values[0] - data_df['rounds'][data_df['rounds']['round']==round_num]['freeze_end'].values[0]) *64

                    is_trade="N/A"#data_df['kills'][(data_df['kills']['round'] == round_num) & (data_df['kills']['victim_name'] == helped_victim)]['isTrade'].values[0] if helped_victim in player_damaged_players_killed else "N/A"

                    alive_teammates=len(data_df['ticks'][(data_df['ticks']['team_clan_name']==name_team_dict[player])&(data_df['ticks']['health'] > 0)&(data_df['ticks']['tick']==last_tick_dmg_frame)])-1

                    damage = player_damages[player_damages['victim_name']==helped_victim]['dmg_health_real'].sum()

                    killed_helped_alive_flag="Killed" if helped_victim in player_damaged_players_killed else "Significantly Assisted" if (damage>=70) & (helped_victim in dead_on_round_end) else "Assisted" if (damage>=50) & (helped_victim in dead_on_round_end) else "Significantly Helped" if (damage>=30) & (helped_victim in dead_on_round_end) else "Helped" if (damage<30) & (helped_victim in dead_on_round_end) else "Survived"
                    
                    help_damage=pd.concat([help_damage,pd.DataFrame([{'RoundProgress':clock_time,'Victim': helped_victim, 'Damage': damage,'TimeElapsed': time_difference_seconds,'KillNumber':kill_number,'IsTrade':is_trade,'KilledHelpedAliveFlag':killed_helped_alive_flag,'PlayerWeapon':player_weapon,'VictimWeapon':victim_weapon,'PlayerTeamEconomy':player_team_economy,'VictimTeamEconomy':victim_team_economy,'AliveTeammates':alive_teammates}])])
                help_damage['RoundEndReason']=data_df['rounds'][data_df['rounds']['round']==round_num]['reason'].values[0]
                help_damage['PlayerTeamWon'] = True if name_team_dict[player] == data_df['rounds']['winner_clan_name'][data_df['rounds']['round'] == round_num].values[0] else False
                player_side=data_df['ticks'][(data_df['ticks']['name'] == player)&(data_df['ticks']['round'] == round_num)]['team_name'].unique()[0]
                help_damage['PlayerSide']=player_side
                # player_team_score=data_df['rounds'][data_df['rounds']['round']==round_num]['ctScore'].values[0] if player_side=='CT'else data_df['rounds'][data_df['rounds']['round']==round_num]['tScore'].values[0]
                # victim_team_score=data_df['rounds'][data_df['rounds']['round']==round_num]['ctScore'].values[0] if player_side=='T'else data_df['rounds'][data_df['rounds']['round']==round_num]['tScore'].values[0]
                player_team_score = data_df['rounds'][(data_df['rounds']['round'] < round_num) & (data_df['rounds']['winner_clan_name'] == name_team_dict[player])].shape[0]
                victim_team_score = round_num - player_team_score - 1

                help_damage['PlayerTeamEconomy']=data_df['rounds'][data_df['rounds']['round']==round_num]['ct_buytype'].values[0] if player_side=="CT" else data_df['rounds'][data_df['rounds']['round']==round_num]['t_buytype'].values[0]
                help_damage['VictimTeamEconomy']=data_df['rounds'][data_df['rounds']['round']==round_num]['t_buytype'].values[0] if player_side=="CT" else data_df['rounds'][data_df['rounds']['round']==round_num]['ct_buytype'].values[0]
                help_damage['PlayerTeamScore']=player_team_score
                help_damage['VictimTeamScore']=victim_team_score
                help_damage['Rating']="?"


                #help_damage

                death_table=pd.DataFrame(columns=["PlayerScore","EnemyScore","PlayerSide","PlayerTeamEconomy","VictimTeamEconomy","KillNumber","KillNumberTeam","HadKit","HadAWP","IsFirstDeath","IsTraded","RoundEndReason","RoundWon","Rating"])
                #DEATH TABLE
                #try:
                    #if not data_df['ticks'][(data_df['ticks']['tick']==end_tick)&(data_df['ticks']['name']==player)]['isAlive'].values[0]:
                if 0 in data_df['ticks'][(data_df['ticks']['round']==round_num)&(data_df['ticks']['name']==player)&(data_df['ticks']['health']==0)]['health'].unique():
                    #print("dead")
                    #TODO: CREATE DEATH TABLE itt tartok 2025.04.18.
                    death_table=pd.DataFrame(columns=["KillNumber","KillNumberTeam","HadKit","HadAWP","IsFirstDeath","IsTraded","RoundEndReason","RoundWon"])
                    #to gather: had kit, had awp, firstdeath, istraded, killnumber, roundendreason, roundwon,,,, idk more
                    death_in_round=data_df['kills'][(data_df['kills']['round']==round_num)].reset_index(drop=True)
                    death_num_in_round=death_in_round[(death_in_round['victim_name']==player)].index[0]+1
                    death_in_team=death_in_round[(death_in_round['victim_team_clan_name']==name_team_dict[player])].reset_index(drop=True)
                    death_in_team=death_in_team[death_in_team['victim_name']==player]
                    death_num_in_team=death_in_team.index[0]+1
                    playerframe_on_death=data_df['ticks'][(data_df['ticks']['tick']==death_in_team['tick'].values[0])&(data_df['ticks']['name']==player)]
                    try:
                        has_defuse=playerframe_on_death['has_defuser'].values[0]
                    except:
                        has_defuse="N/A"
                    is_first_death=True if death_num_in_round==1 else False
                    is_traded="N/A"#True if len(death_in_round[death_in_round['playerTradedName']==player])==1 else False
                    team_won = True if name_team_dict[player] == data_df['rounds']['winner_clan_name'][data_df['rounds']['round'] == round_num].values[0] else False
                    has_awp= "AWP" in  data_df['ticks'][(data_df['ticks']['tick']>=data_df['rounds'][(data_df['rounds']['round']==round_num)]['freeze_end'].values[0])&(data_df['ticks']['tick']<=data_df['rounds'][(data_df['rounds']['round']==round_num)]['freeze_end'].values[0]+20*64)&(data_df['ticks']['name']==player)&(data_df['ticks']['round']==round_num)]['inventory'].explode().dropna().unique().tolist()
                    data={"PlayerScore":player_team_score,"EnemyScore":victim_team_score,"PlayerSide":player_side,"PlayerTeamEconomy":"","VictimTeamEconomy":"","KillNumber":death_num_in_round,"KillNumberTeam":death_num_in_team,"HadKit":has_defuse,"HadAWP":has_awp,"IsFirstDeath":is_first_death,"IsTraded":is_traded,"RoundEndReason":round_end_reason,"RoundWon":team_won,"Rating":"?"}
                    death_table=pd.DataFrame([data])
                    death_table["PlayerSide"] = death_table["PlayerSide"].str.replace('TERRORIST', 'T')
                    death_table['PlayerTeamEconomy']=data_df['rounds'][data_df['rounds']['round']==round_num]['ct_buytype'].values[0] if player_side=="CT" else data_df['rounds'][data_df['rounds']['round']==round_num]['t_buytype'].values[0]
                    death_table['VictimTeamEconomy']=data_df['rounds'][data_df['rounds']['round']==round_num]['t_buytype'].values[0] if player_side=="CT" else data_df['rounds'][data_df['rounds']['round']==round_num]['ct_buytype'].values[0]
                # except:
                #     print(fr"Round: {round_num},End tick: {end_tick}, Player: {player}")
                #     data_df['ticks'][(data_df['ticks']['name']==player)&(data_df['ticks']['round']==round_num)].to_excel("debug.xlsx")
                #death_table
                #print(len(help_damage))

                if len(death_table)!=0:
                    #print(death_table.columns)
                    #try:
                    rating_negative = death_table.head(1).apply(rating_weights.calculate_negative_rating, axis=1).values[0]
                    #except:
                        #death_table.to_excel("bad.xlsx")
                    #rating_negative=death_table['Rating'].values[0]
                else:
                    rating_negative=0
                player_team_economy = data_df['rounds'][data_df['rounds']['round']==round_num]['ct_buytype'].values[0] if player_side=="CT" else data_df['rounds'][data_df['rounds']['round']==round_num]['t_buytype'].values[0]
                player_team_economy = "Pistol" if round_num == 1 else "Pistol" if round_num == 13 else player_team_economy
                if len(help_damage)!=0:
                    help_damage["PlayerSide"] = help_damage["PlayerSide"].str.replace('TERRORIST', 'T')
                    help_damage['Rating'] = help_damage.apply(rating_weights.calculate_positive_rating, axis=1)
                    #print(fr'Saving: "round": {round_num},"Player":{player},"Rating":{help_damage["Rating"].sum()}')
                    
                    data_for_rating_df={"match_src":match,"RoundNum": round_num, "PlayerSide": player_side, "PlayerEconomy": player_team_economy, "team_clan_name": name_team_dict[player], "Player":player,"PositiveRating":help_damage["Rating"].sum(),"NegativeRating":rating_negative,"Rating":help_damage["Rating"].sum()+rating_negative}
                    temp_df_rate=pd.DataFrame([data_for_rating_df])
                    rating_df=pd.concat([rating_df,temp_df_rate])
                    #if (player=='ZywOo') & (round_num==11):
                    # File path of the existing Excel file
                    # file_path = 'new_finalv4.xlsx'

                    # # Read the existing Excel file into a DataFrame
                    # #existing_data = pd.read_excel(file_path) if not first else None
                    # try:
                    #     existing_data = pd.read_excel(file_path)
                    # except:
                    #     existing_data = pd.DataFrame()
                    # help_damage['round']=round_num
                    # help_damage['Player']=player
                    # help_damage['Team']=name_team_dict[player]
                    # # Append the new DataFrame to the existing data
                    # combined_data = pd.concat([existing_data,help_damage], ignore_index=True)
                    
                    # combined_data.to_excel(file_path,index=False)
                    #     #help_damage.to_excel('help_damage_table_sample.xlsx')
                    # first=False
                else:
                    #print(fr'Saving: "round": {round_num},"Player":{player},"Rating":{0}')
                    # if data_df['rounds'][data_df['rounds']['round']==round_num]['tTeam'].values[0]==name_team_dict[player]:
                    #     side="T"
                    # else:
                    #     side="CT"
                    side = player_side
                    won_round=(name_team_dict[player]==data_df['rounds'][data_df['rounds']['round']==round_num]['winner_clan_name'].values[0])
                    if side=="CT":
                        player_buytype=data_df['rounds'][data_df['rounds']['round']==round_num]['ct_buytype'].values[0]
                        enemy_buytype=data_df['rounds'][data_df['rounds']['round']==round_num]['t_buytype'].values[0]
                    else:
                        player_buytype=data_df['rounds'][data_df['rounds']['round']==round_num]['t_buytype'].values[0]
                        enemy_buytype=data_df['rounds'][data_df['rounds']['round']==round_num]['ct_buytype'].values[0]
                    if won_round==True:
                        buytype_multiplier=rating_weights.weights_buytype_win[player_buytype][enemy_buytype]
                    else:
                        buytype_multiplier=rating_weights.weights_buytype_lose[player_buytype][enemy_buytype]
                    # positive_rating=0.5*buytype_multiplier*rating_weights.calculate_score_impact(data_df['rounds'][data_df['rounds']['round']==round_num]['tScore'].values[0],data_df['rounds'][data_df['rounds']['round']==round_num]['ctScore'].values[0])
                    positive_rating=0.5*buytype_multiplier*rating_weights.calculate_score_impact(player_team_score,victim_team_score)
                    data_for_rating_df={"match_src": match,"RoundNum": round_num, "PlayerSide": side, "PlayerEconomy": player_team_economy, "team_clan_name": name_team_dict[player],"Player":player,"PositiveRating":positive_rating,"NegativeRating":rating_negative,"Rating":0+rating_negative}
                    temp_df_rate=pd.DataFrame([data_for_rating_df])
                    rating_df=pd.concat([rating_df,temp_df_rate])
                #if len(death_table)!=0:
                    #death_table['Rating'] = death_table.apply(rating_weightscalculate_negative_rating, axis=1)
    rating_df["Rating"] = rating_df["PositiveRating"] + rating_df["NegativeRating"]

    return rating_df