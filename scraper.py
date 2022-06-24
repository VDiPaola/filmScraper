# imports stuff
import os

from selenium import webdriver
import datetime
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# load usernames
movie_data_json = "movieData.json"
movie_data = {}
with open(movie_data_json, 'r+') as openFile:
    try:
        movie_data = json.load(openFile)
    except ValueError:
        print('Decoding JSON has failed')

# log
logfile = "log.txt"

# get movies in 1080p from 1990 - 2022 in english that have 5+ rating
url = "https://yify.day/movies?keyword=&quality=1080p&genre=&rating=5&year=1990-2022&language=en&order_by=latest"
starting_page = int(os.environ.get('PAGE', 1))

# sets driver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument("disable-arguments");
chrome_options.add_argument("disable-gpu");

browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
browser.delete_all_cookies()


class Movie:
    def __init__(self, _title, _link):
        self.title = _title
        self.link = _link


def log(msg, will_print=False):
    with open(logfile, "a") as f:
        f.write(str(datetime.datetime.now()) + " " + msg + "\n")
    if will_print:
        print(msg)

# get and save movie data
def saveMovie(movie_object):
    if movie_object.title not in movie_data:
        # goto link
        browser.get(movie.link)
        # get torrent hash
        hash_el = WebDriverWait(browser, timeout=3).until(lambda d: d.find_element_by_id("modal-quality-1080p"))
        download_el = hash_el.find_element(By.XPATH, "./../a[1]")
        href = download_el.get_attribute("href")
        hash = href[href.rfind("/") + 1:]
        # save data
        movie_data[movie_object.title] = hash
        with open(movie_data_json, 'w') as json_file:
            json.dump(movie_data, json_file,
                      indent=4,
                      separators=(',', ': '))
        # log
        log("ADDED: " + movie_object.title + " - " + hash)
    else:
        log("UP TO DATE: " + movie_object.title + " already in database", True)


try:
    log("STARTED", True)
    log("MOVIE COUNT: " + str(len(movie_data)), True)
    # load website
    browser.get(url + "&page=" + str(starting_page))
    robotButton = browser.find_elements(By.CSS_SELECTOR, "#verifyForm > div > input")
    if robotButton[0]:
        browser.execute_script('arguments[0].click()', robotButton[0])
    # get number of pages
    pageNum = browser.find_element(By.XPATH, "//a[@href='" + url + "&page=2" + "']"
                                                     "/../../li[position() = (last() - 1)]/a").get_property("innerText")
    for page in range(starting_page, int(pageNum)):
        # get movie links
        log("PAGE: " + str(page) + "/" + str(pageNum) , True)
        movieLinks = browser.find_elements(By.CLASS_NAME, "browse-movie-bottom")
        movies = []
        for movieLink in movieLinks:
            titleEl = movieLink.find_element(By.CLASS_NAME, "browse-movie-title")
            title = titleEl.get_property("innerText")
            year = movieLink.find_element(By.CLASS_NAME, "browse-movie-year").get_property("innerText")
            link = titleEl.get_property("href")

            # append movie data
            movies.append(Movie(title + " (" + year + ")", link))

        # browser.switch_to.new_window('tab')
        for movie in movies:
            saveMovie(movie)

        browser.get(url + "&page=" + str(page+1))

finally:
    # quit
    browser.quit()
    log("ENDED", True)
    log("MOVIE COUNT: " + str(len(movie_data)), True)
