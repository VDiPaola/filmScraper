import datetime
import json

# load usernames
movie_data_json = "movieData.json"

# log
logfile = "log.txt"

def get_movie_data():
    with open(movie_data_json, 'r+') as openFile:
        try:
            return json.load(openFile)
        except ValueError:
            print('Decoding JSON has failed')
            return {}

class Movie:
    def __init__(self, _title, _link):
        self.title = _title
        self.link = _link

def log(msg, will_print=False):
    with open(logfile, "a") as f:
        f.write(str(datetime.datetime.now()) + " " + msg + "\n")
    if will_print:
        print(msg)