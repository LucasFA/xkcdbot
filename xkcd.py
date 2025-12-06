import urllib
import json
import random
import requests
import time


class APIException(Exception):
    def __init__(self, message):
        self.message = message


def getComic(comic_number = None, retries=5):
    suffix = "/" + str(comic_number) if comic_number != None else ""
    for nretries in range(retries):
        query = "https://xkcd.com" + suffix + "/info.0.json"
        print("DEBUG")
        print(query)
        print("DEBUG")

        resp = requests.get(query, timeout=1)
        if resp.status_code == 200:
            return resp.json()
        time.sleep(1)

    raise APIException("Invalid answer from API.")


def getLatestComic(retries = 5):
    return getComic(retries = retries)


def getRandomComic(maxNumber, retries=5):
    rand_num = str(random.randint(1, maxNumber))
    getComic(rand_num, retries)
