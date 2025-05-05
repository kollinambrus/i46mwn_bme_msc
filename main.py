import time
import bcrypt
import streamlit as st
import pandas as pd

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "data_dict" not in st.session_state:
    st.session_state.data_dict = {"header": [], "rounds": pd.DataFrame(), "grenades": pd.DataFrame(), "kills": pd.DataFrame(), "damages": pd.DataFrame(), "bomb": pd.DataFrame(), "smokes": pd.DataFrame(), "infernos": pd.DataFrame(), "weapon_fires": pd.DataFrame(), "ticks": pd.DataFrame(), "new_rating": pd.DataFrame()}

if "stats_df" not in st.session_state:
    st.session_state.stats_df = pd.DataFrame()

if "dem_upload_count" not in st.session_state:
    st.session_state.dem_upload_count = 0

if "dem_list" not in st.session_state:
    st.session_state.dem_list = pd.DataFrame(columns=["map_text","map","team1","team2","score","source","match_page","file_id","include/exclude/delete"])

if "dem_ids_to_analyse" not in st.session_state:
    st.session_state.dem_ids_to_analyse = []

if "hltv_demo_ready_to_download" not in st.session_state:
    st.session_state.hltv_demo_ready_to_download = False

if "dem_id_name" not in st.session_state:
    st.session_state.dem_id_name = pd.DataFrame(columns=["id","name"])

def welcome():
    st.title('Welcome!')

    #st.sidebar.subheader("Counter - Strike: Analytics")
    #st.sidebar.image('resources\logo\counter_strike_analytics.jpeg')


    with st.expander("About this page"):
        st.write("This is the content inside the expander.")
        st.write("You can add any Streamlit components here.")

    #st.file_uploader('Testing config.toml')
    st.write(f"testing secrets.toml: {st.secrets['test']}")

def login():
    @st.dialog("Log in 🔑")
    def login_auth():
        with st.form("my_form", border=False):
            auth_code = st.text_input("Please input your authentication code", help = "Please input your authentication code to log in to the application")# type = "password", 
            if st.form_submit_button("Submit"):
                if bcrypt.checkpw(auth_code.encode('utf-8'), st.secrets['auth_key_hash'].encode("utf-8")):
                    st.success("Successful login.. redirecting in 3 seconds", icon = ":material/check_circle:")
                    time.sleep(3)
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    invalid = st.error("Invalid code, please try again.", icon=":material/priority_high:")
                    


    st.info("To log in to the application, press the below button.", icon=":material/info:")
    
    if st.button("Log in 🔑"):
        login_auth()

def logout():
    st.info("To log out of the application, press the below button.", icon=":material/info:")
    if st.button("Log out ❌"):
        st.session_state.logged_in = False
        st.rerun()

login_page = st.Page(login, title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

def page2():

    @st.experimental_dialog("Cast your vote")
    def vote(item):
        st.write(f"Why is {item} your favorite?")
        reason = st.text_input("Because...")
        if st.button("Submit"):
            st.session_state.vote = {"item": item, "reason": reason}
            st.rerun()

    if "vote" not in st.session_state:
        st.write("Vote for your favorite")
        if st.button("A"):
            vote("A")
        if st.button("B"):
            vote("B")
    else:
        f"You voted for {st.session_state.vote['item']} because {st.session_state.vote['reason']}"

def page1():
    st.write('bsd')

def page3():
    st.write('csd')
def page4():
    st.write('csd')
def page5():
    st.write('csd')
def page6():
    st.write('csd')
def page7():
    st.write('csd')
def page8():
    st.write('csd')
def page9():
    st.write('csd')
def page10():
    st.write('csd')
def page11():
    st.write('csd')
def page12():
    st.title('AI Module - Evaluate player actions')
    st.write('Coming soon.')

vis_heatmap = st.Page("pages_py/visualisation_heatmap.py", title = "Heatmaps", icon=":material/bubble_chart:")
vis_util = st.Page("pages_py/visualisation_utility.py", title = "Utility", icon=":material/menu_book:")
vis_replay = st.Page("pages_py/visualisation_replay.py", title = "Replay", icon=":material/replay:")

stat_dashboard = st.Page("pages_py/stats_dashboard.py", title = "Dashboard", icon=":material/team_dashboard:")
stat_new_rating = st.Page("pages_py/new_rating_page.py", title = "New Rating", icon=":material/star:")

ai_clutch = st.Page("pages_py/ai_classification_page.py", title = "Clutch prediction", icon=":material/repeat_one:")
ai_structure = st.Page("pages_py/ai_clustering_page.py", title = "Structure analysis", icon=":material/donut_small:")
ai_evaluate = st.Page(page12, title = "Evaluation of player actions", icon=":material/person_search:")

# default layout settings
st.set_page_config(layout="wide",page_title='Counters - An interactive CS analyzing web app', page_icon='resources/logo/counter_strike_analytics_favicon.png')
st.sidebar.subheader("Counters")

#pg = st.navigation([st.Page(page1), st.Page(page2)])
if st.session_state.logged_in:
    pg = st.navigation(
            {
                "Data Source": [st.Page("pages_py/upload_datasource.py", title = "Upload data source(s)", icon=":material/folder_open:"),st.Page("pages_py/choose_datasource.py", title = "Choose data source(s)", icon=":material/check_circle:")],
                "Statistics": [stat_dashboard, stat_new_rating],
                "Visualizations": [vis_heatmap, vis_util, vis_replay],
                "AI solutions": [ai_clutch, ai_structure, ai_evaluate],
                "Log out": [logout_page]
            }
        )
else:
    pg = st.navigation([st.Page(welcome, title="Welcome", default=True, icon = ":material/waving_hand:"),login_page])
pg.run()
st.sidebar.info("Demo version...", icon=":material/warning:")


