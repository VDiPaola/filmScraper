# imports stuff
import os

from selenium import webdriver
import datetime
import time
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
import re

from helpers import movie_data_json
from helpers import get_movie_data
from helpers import Movie
from helpers import log

# get top 100 hd movies and tv shows
# https://rargb.to/movies/?order=seeders&by=DESC
base_url = "https://tpb.one/search.php"
categories = ["207", "208"]
searchCondition = os.environ.get('SEARCH', False)
min_seeders = 5

# sets driver
chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--headless')
chrome_options.add_argument("disable-arguments");
chrome_options.add_argument("disable-gpu");

browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
browser.delete_all_cookies()

movie_data = get_movie_data()


# get and save movie data
def saveMovie(title, hash):
    if title not in movie_data and hash not in movie_data.values():
        # save data
        movie_data[title] = hash
        with open(movie_data_json, 'w') as json_file:
            json.dump(movie_data, json_file,
                      indent=4,
                      separators=(',', ': '))
        # log
        log("ADDED: " + title + " - " + hash)
    else:
        log("UP TO DATE: " + title + " already in database", True)



try:
    log("STARTED tpb", True)
    log("MOVIE COUNT: " + str(len(movie_data)), True)
    #get urls
    urls = []
    for category in categories:
        if searchCondition:
            urls.append(base_url + "?q=" + searchCondition + "&cat=" + category)
        else:
            urls.append(base_url + "?q=top100:" + category)

    # load website
    browser.get("http://www.google.com")
    time.sleep(10)
    for url in urls:
        browser.get(url)

        # get movie links
        movieList = browser.find_elements(By.CLASS_NAME, "list-entry")
        for movieRow in movieList:
            # get full title element
            titleEl = movieRow.find_element(By.CSS_SELECTOR, ".item-title a")
            full_title = titleEl.get_property("innerText")
            full_title = full_title.replace(".", " ")
            # find quality in title
            hdIndex = full_title.find("1080p")
            hd2Index = full_title.find("720p")
            if hdIndex >= 0 or hd2Index >= 0:
                title = full_title[:hdIndex] if hdIndex >= 0 else full_title[:hd2Index]
                if title[-1] != " ":
                    title = title[:len(title)-2]

                title_data = full_title[len(title)-1:].lower()

                # check its good rip and trusted and min seeders
                good_rip = "web" in title_data or "blu" in title_data
                trusted = False
                seeders = int(movieRow.find_element(By.CSS_SELECTOR, ".item-seed").get_property("innerText"))
                try:
                    movieRow.find_element(By.CSS_SELECTOR, ".item-icons > img")
                    trusted = True
                except NoSuchElementException:
                    trusted = False

                if good_rip and trusted and seeders >= min_seeders:
                    # find year
                    year_match = re.search("\([0-9]{4}\)", title)
                    year_match2 = re.search(" [0-9]{4} ", title)
                    if year_match or year_match2:
                        # format title and year
                        year = year_match.group() if year_match else year_match2.group().strip()

                        title = title[:year_match.start()] if year_match else title[:year_match2.start()]
                        if title[-1] != " ":
                            title += " "
                        if year[0] == "(":
                            title += year
                        else:
                            title += "(" + year + ")"
                    #append quality to title if its 720p
                    title = title.strip()
                    if hd2Index >= 0:
                        title += " [720p]"
                    #get hash
                    hashEl = movieRow.find_element(By.CSS_SELECTOR, ".item-icons > a")
                    hash = hashEl.get_attribute("onclick").split("'")[1]

                    # save movie
                    #saveMovie(title, hash)
                    print(title)
                    print(hashEl.get_attribute("href").split("&dn=")[0].split(":")[-1])

finally:
    # quit
    #browser.quit()
    log("ENDED tpb", True)
    log("MOVIE COUNT: " + str(len(movie_data)), True)
