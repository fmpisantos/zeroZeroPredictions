# Path: requests.py
from datetime import datetime
import json
import os
import requests
import config

# Get previous day
def getPreviousDay(date = None):
    # If date empty, return today
    if date == None or date == "":
        date = datetime.now().strftime("%Y-%m-%d")
    # Get previous day
    date = date.split('-')
    year = int(date[0])
    month = int(date[1])
    day = int(date[2])
    if day == 1:
        if month == 1:
            year -= 1
            month = 12
            day = 31
        else:
            month -= 1
            day = 31
    else:
        day -= 1
    return f"{year}-{month}-{day<10 and '0'+str(day) or day}"

# read JSON file
def readJsonFile(filename):
    with open(filename) as f:
        return json.load(f)
        
# check if dictionary has key
def hasKey(dictionary, key):
    if key in dictionary:
        return True
    else:
        return False

# string to uppercase
def stringToUppercase(string):
    return string.upper()

# create directory if not exists in path
def createDirectory(path = ""):
    if not os.path.exists(path):
        os.makedirs(path)

# write dictionary to file
def writeToFile (data, filename):
    createDirectory(os.path.dirname(filename))
    with open(filename, 'a') as outfile:
        json.dump(data, outfile, indent=4)

# parse request response
def parseRequestResponse(response, request = ""):
    if response.status_code == 200:
        json = response.json()
        if json['results'] > 0:
            json = json['response']
            _print(json)
            writeToFile(json, config.getOutput(request))
            return json
        if json['errors'] != None and len(json['errors']) > 0:
            _print(json)
            writeToFile(json, config.getErrorOutput(request))
            return None
    json = response.json()
    _print(json)
    writeToFile(json, config.getErrorOutput(request))
    return None

# convert ../zeroZero/utils.py/request to python3  
def _request(url = "", headers = config.headers, method = config.GET):
    if method == config.GET:
        return parseRequestResponse(requests.get(config.getUrl(url), headers = headers), url)
    elif method == config.POST:
        return parseRequestResponse(requests.post(config.getUrl(url), headers = headers), url)
    elif method == config.PUT:
        return parseRequestResponse(requests.put(config.getUrl(url), headers = headers), url)
    else:
        return None

# get fixture statistics
def getFixtureStatistics(fixtureId = -1):
    return _request(f"v3/fixtures/statistics?fixture={fixtureId}")

# get team statistics
def getTeamStatistics(team = -1, league = -1, season = -1, date = None):
    return _request(f"v3/teams/statistics?team={team}&league={league}&season={season}{f'&date={date}' if date != None else ''}")

def _print(data):
    if config.printToConsole:
        print(data)

def loadFromDB(filename = config.dbLocation):
    return readJsonFile(filename)