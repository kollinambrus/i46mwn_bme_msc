import streamlit as st

def gather_matches(map_str: str) -> list:
    if map_str != "All":
        map_str = "de_" + map_str.lower().replace(' ','')

        match_idx= list(st.session_state.dem_list[(st.session_state.dem_list['map_text'] == map_str) & (st.session_state.dem_list['include/exclude/delete'] == "Include")]['file_id'].unique())
        return list(st.session_state.dem_id_name[st.session_state.dem_id_name['id'].isin(match_idx)]['name - id'])
    else:
        match_idx= list(st.session_state.dem_list[(st.session_state.dem_list['include/exclude/delete'] == "Include")]['file_id'].unique())
        return list(st.session_state.dem_id_name[st.session_state.dem_id_name['id'].isin(match_idx)]['name - id'])
    
def gather_max_round(match_names: str) -> int:
    match_idx = st.session_state.dem_id_name[st.session_state.dem_id_name['name - id'].isin(match_names)]['id'].unique()
    if len(match_idx) < 1:
        return 2
    result= st.session_state.data_dict['rounds'][st.session_state.data_dict['rounds']['match_src'].isin(match_idx)]['round'].max()
    return int(result)

def gather_players(match_names: str) -> list:
    # match_names = [x.split(" - ")[-1] for x in match_names]
    print(match_names)
    match_idx = st.session_state.dem_id_name[st.session_state.dem_id_name['name - id'].isin(match_names)]['id'].unique()

    return list(st.session_state.data_dict['ticks'][st.session_state.data_dict['ticks']['match_src'].isin(match_idx)]['name'].sort_values(ascending = True).unique())

def gather_match_ids(match_names):
    pass