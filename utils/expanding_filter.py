import streamlit as st
import pandas as pd
import numpy as np
from datetime import time

from functions.query_demos import gather_matches, gather_max_round, gather_players

class ExpandingVisFilter():

    def __init__(self):
        self.query_text = ""

        col1, col2 = st.columns(2)

        self.map_name = col1.selectbox("Map",["Dust2", "Mirage", "Inferno", "Nuke", "Train", "Overpass", "Vertigo", "Ancient", "Anubis"])
        self.match_list = col2.multiselect("Matches", gather_matches(self.map_name))
        self.match_idx = [x.split(' - ')[-1] for x in self.match_list]
        
        with st.expander("Apply filters"):
            col1_1, col2_1 = st.columns(2)

            self.side_name = col1_1.selectbox("Side", ["Both", "CT", "T"])
            self.game_state = col1_1.selectbox("Game State", ["All", "Bomb planted", "Clutch situation - coming soon", "Before first kill - coming soon"])
            self.round_type = col2_1.selectbox("Round Type", ["All", "Pistol", "Rest", "Full Eco", "Semi Eco", "Semi Buy", "Full Buy"]) # todo: based on equipment value: eco, semi eco, force, full buy
            self.player_name = col2_1.multiselect("Player Name", gather_players(self.match_list))
            self.round_time = st.slider("Round time", time(00,00), time(2,55), value=(time(00, 00), time(2,55)))

            # st.write(st.session_state.data_dict['ticks'].columns)

    def create_filter(self):
        # filtered_df = df.query("age > 25 and city == 'Chicago'")
        self.query_text = ""
        if self.side_name != "Both":
            print("?")
            print(self.side_name == "T")
            print("?")
            if self.side_name == "T":
                self.side_name = "TERRORIST"
            self.query_text += f"team_name == '{self.side_name}'"
        if self.game_state != "All":
            self.query_text += " and is_bomb_planted"
        if self.round_type == "Pistol":
            self.query_text += " and (round == 1 or round == 13)"
        if len(self.player_name) > 0:
            self.query_text += " and ( "
            for player_name in self.player_name:
                self.query_text += f"name == '{player_name}' or "
            self.query_text = self.query_text[:-3] + ")" # delete last or

        self.match_idx = [x.split(' - ')[-1] for x in self.match_list]
        self.query_text += " and match_src in @match_idx"

        if self.query_text.startswith(' and'):
            self.query_text = self.query_text[4:]
        
        print("!!!! query")
        print(self.query_text)
        print("!!!! query")

    def feed_match_idx(self) -> list:
        return [x.split(' - ')[-1] for x in self.match_list]
    
    def feed_match_map(self) -> str:
        return ("de_" + self.map_name).replace(' ','').lower()
    
class ExpandingVisFilterNewRating():

    def __init__(self):
        self.query_text = ""

        col1, col2 = st.columns(2)

        self.map_name = col1.selectbox("Map",["All", "Dust2", "Mirage", "Inferno", "Nuke", "Train", "Overpass", "Vertigo", "Ancient", "Anubis"])
        self.match_list = col2.multiselect("Matches", gather_matches(self.map_name))
        self.match_idx = [x.split(' - ')[-1] for x in self.match_list]
        
        with st.expander("Apply filters"):
            col1_1, col2_1 = st.columns(2)

            self.side_name = col1_1.selectbox("Side", ["Both", "CT", "T"])
            # self.game_state = col1_1.selectbox("Game State", ["All", "Bomb planted", "Clutch situation - coming soon", "Before first kill - coming soon"])
            self.round_type = col2_1.selectbox("Round Type", ["All", "Pistol", "Full Eco", "Semi Eco", "Semi Buy", "Full Buy"]) # todo: based on equipment value: eco, semi eco, force, full buy
            self.player_name = col2_1.multiselect("Player Name", gather_players(self.match_list))
            # self.round_time = st.slider("Round time", time(00,00), time(2,55), value=(time(00, 00), time(2,55)))

            # st.write(st.session_state.data_dict['ticks'].columns)

    def create_filter(self):
        # filtered_df = df.query("age > 25 and city == 'Chicago'")
        self.query_text = ""
        if self.side_name != "Both":
            print("?")
            print(self.side_name == "T")
            print("?")
            if self.side_name == "T":
                self.side_name = "TERRORIST"
            self.query_text += f"PlayerSide == '{self.side_name}'"
        # if self.game_state != "All":
            # self.query_text += " and is_bomb_planted"
        if self.round_type != "All":
            self.query_text += f" and PlayerEconomy == '{self.round_type}'"
        if len(self.player_name) > 0:
            self.query_text += " and ( "
            for player_name in self.player_name:
                self.query_text += f"Player == '{player_name}' or "
            self.query_text = self.query_text[:-3] + ")" # delete last or

        self.match_idx = [x.split(' - ')[-1] for x in self.match_list]
        self.query_text += " and match_src in @match_idx"

        if self.query_text.startswith(' and'):
            self.query_text = self.query_text[4:]
        
        print("!!!! query")
        print(self.query_text)
        print("!!!! query")

    def feed_match_idx(self) -> list:
        return [x.split(' - ')[-1] for x in self.match_list]
    
    def feed_match_map(self) -> str:
        return ("de_" + self.map_name).replace(' ','').lower()
    
class ExpandingVisFilterUtility():

    def __init__(self):
        self.query_text = ""

        col1, col2 = st.columns(2)

        self.map_name = col1.selectbox("Map",["Dust2", "Mirage", "Inferno", "Nuke", "Train", "Overpass", "Vertigo", "Ancient", "Anubis"])
        self.match_list = col2.multiselect("Matches", gather_matches(self.map_name))
        self.match_idx = [x.split(' - ')[-1] for x in self.match_list]
        
        with st.expander("Apply filters"):
            col1_1, col2_1 = st.columns(2)

            self.side_name = col1_1.selectbox("Side", ["Both", "CT", "T"])
            # self.game_state = col1_1.selectbox("Game State", ["All", "Bomb planted", "Clutch situation - coming soon", "Before first kill - coming soon"])
            self.round_type = col2_1.selectbox("Round Type", ["All", "Pistol", "Rest", "Full Eco", "Semi Eco", "Semi Buy", "Full Buy"]) # todo: based on equipment value: eco, semi eco, force, full buy
            self.player_name = col2_1.multiselect("Player Name", gather_players(self.match_list))
            self.utility_type = col1_1.multiselect("Utility Type", st.session_state.data_dict['grenades']['grenade_type'].dropna().unique())#,st.session_state.data_dict['grenades']['grenade_type'].dropna().unique())
            self.round_time = st.slider("Round time", time(00,00), time(2,55), value=(time(00, 00), time(2,55)))

            # st.write(st.session_state.data_dict['ticks'].columns)

    def create_filter(self):
        # filtered_df = df.query("age > 25 and city == 'Chicago'")
        self.query_text = ""
        if self.side_name != "Both":
            print("?")
            print(self.side_name == "T")
            print("?")
            if self.side_name == "T":
                self.side_name = "TERRORIST"
            self.query_text += f"team_name == '{self.side_name}'"
        # if self.game_state != "All":
        #     self.query_text += " and is_bomb_planted"
        if self.round_type == "Pistol":
            self.query_text += " and (round == 1 or round == 13)"
        if len(self.player_name) > 0:
            self.query_text += " and ( "
            for player_name in self.player_name:
                self.query_text += f"thrower == '{player_name}' or "
            self.query_text = self.query_text[:-3] + ")" # delete last or
        if len(self.utility_type) > 0:
            self.query_text += " and ( "
            for utility_type in self.utility_type:
                self.query_text += f"grenade_type == '{utility_type}' or "
            self.query_text = self.query_text[:-3] + ")" # delete last or
        


        self.match_idx = [x.split(' - ')[-1] for x in self.match_list]
        self.query_text += " and match_src in @match_idx"

        if self.query_text.startswith(' and'):
            self.query_text = self.query_text[4:]
        
        print("!!!! query")
        print(self.query_text)
        print("!!!! query")

    def feed_match_idx(self) -> list:
        return [x.split(' - ')[-1] for x in self.match_list]
    
    def feed_match_map(self) -> str:
        return ("de_" + self.map_name).replace(' ','').lower()
    
class ExpandingVisFilterReplay():

    def __init__(self):
        self.query_text = ""

        col1, col2 = st.columns(2)

        self.map_name = col1.selectbox("Map",["Dust2", "Mirage", "Inferno", "Nuke", "Train", "Overpass", "Vertigo", "Ancient", "Anubis"])
        self.match_list = col2.multiselect("Matches", gather_matches(self.map_name))
        self.match_idx = [x.split(' - ')[-1] for x in self.match_list]

        self.round_num = st.slider("Round Number", 1, gather_max_round(self.match_list), value = 1)

            # st.write(st.session_state.data_dict['ticks'].columns)

    def create_filter(self):
        # filtered_df = df.query("age > 25 and city == 'Chicago'")
        self.query_text = ""
        if self.round_num > 0:
            self.query_text += f"round == {self.round_num}"

        self.match_idx = [x.split(' - ')[-1] for x in self.match_list]
        self.query_text += " and match_src in @match_idx"

        if self.query_text.startswith(' and'):
            self.query_text = self.query_text[4:]
        
        print("!!!! query")
        print(self.query_text)
        print("!!!! query")

    def feed_match_idx(self) -> list:
        return [x.split(' - ')[-1] for x in self.match_list]
    
    def feed_match_map(self) -> str:
        return ("de_" + self.map_name).replace(' ','').lower()
    
class ExpandingVisFilterAI():

    def __init__(self):
        self.query_text = ""

        col1, col2 = st.columns(2)

        self.map_name = col1.selectbox("Map",["All", "Dust2", "Mirage", "Inferno", "Nuke", "Train", "Overpass", "Vertigo", "Ancient", "Anubis"])
        self.match_list = col2.multiselect("Matches", gather_matches(self.map_name))
        self.match_idx = [x.split(' - ')[-1] for x in self.match_list]
        
            # st.write(st.session_state.data_dict['ticks'].columns)

    def create_filter(self):
        # filtered_df = df.query("age > 25 and city == 'Chicago'")
        self.query_text = ""

        self.match_idx = [x.split(' - ')[-1] for x in self.match_list]
        self.query_text += " and match_src in @match_idx"

        if self.query_text.startswith(' and'):
            self.query_text = self.query_text[4:]
        
        print("!!!! query")
        print(self.query_text)
        print("!!!! query")

    def feed_match_idx(self) -> list:
        return [x.split(' - ')[-1] for x in self.match_list]
    
    def feed_match_map(self) -> str:
        return ("de_" + self.map_name).replace(' ','').lower()
    
class ExpandingVisFilterDashBoard():

    def __init__(self):
        self.query_text = ""

        col1, col2 = st.columns(2)

        self.map_name = col1.selectbox("Map",["All","Dust2", "Mirage", "Inferno", "Nuke", "Train", "Overpass", "Vertigo", "Ancient", "Anubis"])
        self.match_list = col2.multiselect("Matches", gather_matches(self.map_name))
        self.match_idx = [x.split(' - ')[-1] for x in self.match_list]
        
        with st.expander("Apply filters"):
            col1_1, col2_1 = st.columns(2)

            self.side_name = col1_1.selectbox("Side", ["Both", "CT", "T"])
            # self.game_state = col1_1.selectbox("Game State", ["All", "Bomb planted", "Clutch situation - coming soon", "Before first kill - coming soon"])
            # self.round_type = col2_1.selectbox("Round Type", ["All", "Pistol", "Rest", "Full Eco", "Semi Eco", "Semi Buy", "Full Buy"]) # todo: based on equipment value: eco, semi eco, force, full buy
            self.player_name = col2_1.multiselect("Player Name", gather_players(self.match_list))
            #self.round_time = st.slider("Round time", time(00,00), time(2,55), value=(time(00, 00), time(2,55)))

            # st.write(st.session_state.data_dict['ticks'].columns)

    def create_filter(self):
        # filtered_df = df.query("age > 25 and city == 'Chicago'")
        self.query_text = ""
        self.for_average_query = ""
        if self.side_name != "Both":
            print("?")
            print(self.side_name == "T")
            print("?")
            if self.side_name == "T":
                self.side_name = "TERRORIST"
            self.query_text += f"team_name == '{self.side_name}'"
            self.for_average_query += f"team_name == '{self.side_name}'"
        else:
            self.query_text += "team_name == 'all'"
            self.for_average_query += "team_name == 'all'"
        if len(self.player_name) > 0:
            self.query_text += " and ( "
            for player_name in self.player_name:
                self.query_text += f"name == '{player_name}' or "
            self.query_text = self.query_text[:-3] + ")" # delete last or

        self.match_idx = [x.split(' - ')[-1] for x in self.match_list]
        self.query_text += " and match_src in @match_idx"

        if self.query_text.startswith(' and'):
            self.query_text = self.query_text[4:]
        if self.for_average_query.startswith(' and'):
            self.for_average_query = self.for_average_query[4:]
        
        print("!!!! query")
        print(self.query_text)
        print(self.for_average_query)
        print("!!!! query")

    def feed_match_idx(self) -> list:
        return [x.split(' - ')[-1] for x in self.match_list]
    
    def feed_match_map(self) -> str:
        return ("de_" + self.map_name).replace(' ','').lower()