import time
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from fake_useragent import UserAgent

class HLTVDemoParser():
    def __init__(self, from_date, to_date, maps, match_type, stars) -> None:
        self.from_date = from_date
        self.to_date = to_date
        self.maps = maps
        self.match_type = match_type
        self.stars = stars
        self.downloaded_files = {}

    def get_soup(self, url):
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            #options.add_argument('--no-startup-window')
            options.add_argument('--disable-popup-blocking')
            options.add_argument('--disable-notifications')
            options.add_argument('--disable-background-timer-throttling')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-software-rasterizer')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-infobars')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-setuid-sandbox')
            ua = UserAgent()
            userAgent = ua.random
            options.add_argument(f'user-agent={userAgent}')
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            driver_soup = BeautifulSoup(driver.page_source, features="lxml")
            driver.quit()
            return driver_soup
    
    def get_matchpage_links(self):
            soup = self.soup_object
            matchpage_list = []                                             # Create a empty list to store the matchpage links
            match_soup = soup.find_all("div", {"class": "result-con"})      # Soup containing all matches on the page
            for match in match_soup:                                        # Looping thru all mathches found and getting the matchpage links
                div = match.find('a')
                href = div['href']
                matchpage_list.append('https://www.hltv.org' + href)                                 # Appending links to list
            pagination = soup.find("div", {"class": "pagination-component pagination-top"})
            pagination = int(pagination.span.text.strip().split(' ')[-1])   # Checking for pagination info to see if there are more results
            #self.ui.plaintextedit_logging.appendPlainText(f'There are {pagination} matches.')
            if pagination > 100:                                            # Looping thru remaining pages
                for i in range(100, pagination, 100):
                    offset=i
                    filtering_url = self.filtering_url + f'&offset={offset}'
                    soup = self.get_soup(filtering_url)
                    match_soup = soup.find_all("div", {"class": "result-con"})
                    for match in match_soup:
                        div = match.find('a')
                        href = div['href']
                        matchpage_list.append('https://www.hltv.org' + href)
            return matchpage_list

    def gather_matches(self):
            self.create_matches_link()
            self.soup_object = self.get_soup(self.filtering_url)
            self.match_page_links = self.get_matchpage_links()
            #print(self.match_page_links)
            # for i in range(len(self.match_page_links)):
            #     self.ui.plaintextedit_logging.appendPlainText(self.match_page_links[i])
            #     item = QListWidgetItem(self.match_page_links[i])
            #     item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            #     item.setCheckState(Qt.Checked)
            #     self.ui.lstwdgt_matches.addItem(item)
            # self.ui.btn_download_files.setEnabled(True)
            return self.match_page_links

    def create_matches_link(self):
            map_dict = {'All': 'All', 'Mirage': 'de_mirage', 'Season': 'de_season', 'Dust2': 'de_dust2', 'Cache': 'de_cache', 'Inferno': 'de_inferno', 'Nuke': 'de_nuke', 'Train': 'de_train', 'Cobblestone': 'de_cobblestone', 'Overpass': 'de_overpass', 'Tuscan': 'de_tuscan', 'Vertigo': 'de_vertigo', 'Ancient': 'de_ancient', 'Anubis': 'de_anubis'}
            star_dict = {'1 or more': '1', '2 or more': '2', '3 or more': '3', '4 or more': '4', '5': '5'}
            map_names = [map_dict[x] for x in self.maps]
            match_type = 'Lan' if self.match_type == 'LAN Only' else 'Online' if self.match_type == 'Online' else 'all'
            filtering_url = f'https://www.hltv.org/results?content=demo'
            
            filtering_url += f'&startDate={self.from_date}'# if start_date not in self.preset_dates else ''
            filtering_url += f'&endDate={self.to_date}'# if (end_date not in self.preset_dates) & (end_date!='') else ''
            for map_name in map_names:
                if map_name != 'All':
                    filtering_url += f'&map={map_name}'
            filtering_url += f'&stars={star_dict[self.stars]}' if self.stars in star_dict.keys() else ''
            filtering_url += f'&matchType={match_type}' if match_type != 'all' else ''

            self.filtering_url = filtering_url
            print("!!!")
            print(self.filtering_url)
            print("!!!")

    def download_demos(self):
            for match in set(self.match_page_links):
                self.download_demo(match)
            return self.downloaded_files

    def download_demo(self, match):
            path = "F:\\cs_analytics_private\\cs_analytics_private\\DOWNLOADED_DIR"
            # Convert the relative path to an absolute path
            path = os.path.abspath(os.path.join('.', 'DOWNLOADED_DIR'))
            print(path)
            #path = r'C:\Programming\csgo_demo\demos_rar'
            soup = self.get_soup(match)
            match_a = soup.find("a", {"class": "stream-box"})
            try:
                end_url = match_a['data-demo-link']
                download_url = 'https://www.hltv.org' + end_url
                options = webdriver.ChromeOptions()
                ua = UserAgent()
                userAgent = ua.random
                #options.add_argument('--no-startup-window')
                options.add_argument('--disable-popup-blocking')
                options.add_argument('--disable-notifications')
                options.add_argument('--disable-background-timer-throttling')
                options.add_argument(f'user-agent={userAgent}')
                options.add_argument('--headless')#=new')
                options.add_argument('--disable-gpu')
                options.add_argument('--disable-software-rasterizer')
                options.add_argument('--disable-extensions')
                prefs= {"download.default_directory":path}
                #prefs = {"download.default_directory":"E:\parsed_demos\.raw_demo"}
                #prefs = {"download.default_directory":self.ui.lineedit_download_folder.text()}
                options.add_experimental_option("prefs",prefs)
                driver = webdriver.Chrome(options=options)
                driver.get(download_url)
                print(f'downloading match {match}')
                print(f'from {download_url}')
                #print(f'sleeping for {sleep_time} seconds waiting for download')
                while True:
                    time.sleep(1)  # Check every 1 second
                    files = os.listdir(path)
                    if files:
                        last_modified_file = max(os.listdir(path), key=lambda f: os.path.getmtime(os.path.join(path, f)))
                    else:
                         continue
                    if last_modified_file.endswith('.crdownload'):
                        continue
                    else:
                        break
                #time.sleep(sleep_time)
                print('finished downloading')
                self.downloaded_files[last_modified_file] = match
                driver.quit()
            except Exception as e:
                print('Demo url not found or cloudflare protection')
                print(str(e))
