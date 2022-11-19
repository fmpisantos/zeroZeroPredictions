import sys
import time
import signal
sys.path.append("../")
from config import *
from utils import *

biggerTheBetter             = [ 'notDrawPrediction','averageTeam.form',
                                'averageTeam.att', 'averageTeam.goals', 
                                'averageTeam.league.fixtures.notDrawPrediction',
                                'averageTeam.notClearSheets', 'averageTeam.notFailedToScore', 
                                'comparison.poisson_distribution', 'comparison.goals', 
                                'comparison.total' ]
biggestDifference           = [ 'averageTeam.form' ]
singleBigger                = [ 'averageTeam.form','averageTeam.att', 
                                'averageTeam.goals', 'averageTeam.league.minutePercentAverage',
                                'averageTeam.notClearSheets' ]
biggestDifferenceAttVSDef   = [ 'averageTeam.att' ]
smallestTheBest             = [ 'averageTeam.def' ]
singleSmallest              = [ 'averageTeam.def' ]

# catch ctrl+c and crash
def signalHandler(signal, frame):
    print('You pressed Ctrl+C!')
    writeToFile(top5, getOutput('top5'))
    sys.exit(0)

signal.signal(signal.SIGINT, signalHandler)

def function(tag, min, tagValue1 = None, tagValue2 = None, tagValue3 = None):
    if tag in biggerTheBetter and tagValue3 > min:
        return False
    if tag in biggestDifference and abs(tagValue1 - tagValue2) > min:
        return False
    if tag in singleBigger and tagValue1 > min and tagValue2 > min:
        return False
    if tag in smallestTheBest and tagValue3 < min:
        return False
    if tag in singleSmallest and tagValue1 < min and tagValue2 < min:
        return False
    return True

def execByType(type, min, tagValue1 = None, tagValue2 = None):
    if type == 0:
        return tagValue1 >= min
    if type == 1:
        return abs(tagValue1 - tagValue2) > min
    if type == 2:
        return tagValue1 <= min

def calculateBruteForce(fixtures = [], tags = []):
    if len(fixtures) == 0 or len(tags) == 0:
        return None
    greenGames = 0
    redGames = 0
    for fixture in fixtures:
        predictedGreen = True
        for tag in tags:
            if tag['tag'] in fixture:
                home = tag['tag'].replace("averageTeam.", "homeTeam.")
                away = tag['tag'].replace("averageTeam.", "awayTeam.")
                if "Team" in tag['tag']:
                    if execByType(tag['tag'], tag['val'], fixture[home], fixture[away],fixture[tag['tag']]) == False:
                        predictedGreen = False
                        break
                else:
                    if execByType(tag['tag'], tag['val'], fixture[tag['tag'], None]) == False:
                        predictedGreen = False
                        break
        if predictedGreen:
            if fixture['green']:
                greenGames += 1
            else:
                redGames += 1
    return greenGames, redGames

# calculate brute force for every group of tags with all the possible tags defined as a single entry to the tags array
def calculateBruteForceDescriptiveTags(fixtures = [], tags = []):
    if len(fixtures) == 0 or len(tags) == 0:
        return None
    # games bot betted and won
    wonBets = 0
    # games bot betted and lost
    lostBets = 0
    for fixture in fixtures:
        predictionGreen = True
        for tag in tags:
            if tag['tag'] in fixture:
                team2 = None
                if 'tag2' in tag:
                    if tag['tag2'] in fixture:
                        team2 = fixture[tag['tag2']]
                if ((team2 != None and team2 > 0 )or team2 == None) and fixture[tag['tag']] > 0:
                    if tag['val'] != None and execByType(tag['type'], tag['val'], fixture[tag['tag']], team2 ) == False:
                        predictionGreen = False
                        break
        if predictionGreen:
            if fixture['green']:
                wonBets += 1
            else:
                lostBets += 1
    return wonBets, lostBets

# calculate increment for a tag
def getIncrement(tag):
    inc = 0.1 if "increment" not in tag else tag["increment"]
    if tag['tag'] in smallestTheBest or tag['tag'] in singleSmallest:
        return inc * -1
    return inc

# calculate increment for tag with type defined
def getIncrementWithType(tag):
    inc = 0.1 if "increment" not in tag else tag["increment"]
    if tag['type'] == 2:
        return inc * -1
    return inc

def checkIfGreensBiggerThanAnyOther(result, results):
    if len(results) < 5:
        results += [result]
        return
    for r in results:
        if r["percent"] > result["percent"]:
            r = result

def incrementTag(tags, idx):
    if idx == -1 or idx > len(tags) - 1:
        return False
    tag = tags[idx]
    if tag["val"] == None: 
        tag["val"] = tag["min"] 
    tag["val"] += tag["inc"]
    if ( tag["inc"] > 0 and tag["val"] >= tag["max"] ) or ( tag["inc"] < 0 and tag["val"] <= tag["max"] ):
        tag["val"] = tag["min"]
        incrementTag(tags, idx + 1)
    return True

# create a loop that iterates over all the tags with all combinations and all min and max values and calls calculateBruteForce
def loopTags(tags, fixtures, maxIterations = 0):
    global top5
    top5 = []
    results = []
    itNum = 0
    timeSoFar = 0
    while True:
        timeStart = time.time()
        itNum += 1
        if not incrementTag(tags, 0):
            break
        # call calculateBruteForce
        greens, reds = calculateBruteForceDescriptiveTags(fixtures, tags)
        # replace top 5 if needed
        result = {"greens": greens, "reds": reds, "percent" : greens / (greens + (reds if reds > 0 else 1)), "tags": tags, "nGames": len(fixtures)}
        checkIfGreensBiggerThanAnyOther(result, top5)
        # save results
        results += result
        timeEnd = time.time()
        timeSoFar = timeSoFar + (timeEnd - timeStart)
        print(f"Iteration {itNum} of {maxIterations}. Time left (minutes): {(timeSoFar / itNum * (maxIterations - itNum)/60)}.", end="\r")

    return results, top5

def getNumberOfIterations(tags):
    iterations = 1
    for tag in tags:
        iterations *= (tag["max"] - tag["min"]) / abs(tag["inc"])
    return iterations

def main(path, tagPath = None):
    fixtures = loadFromDB(path)
    if fixtures is None:
        return None
    fixtures = [f for f in fixtures if f['homeTeam.total'] + f['awayTeam.total'] > minNumberOfGames]
    if tagPath == None:
        tags = loadFromDB(f"{getOutputFolder('helper')}bruteForce.json")
    else:
        tags = loadFromDB(tagPath)
    tags = [{**tag, **{"val": None,"inc": getIncrementWithType(tag)}} for tag in tags]
    results, top5 = loopTags(tags, fixtures, getNumberOfIterations(tags))
    writeToFile(results, getOutput('results'))
    writeToFile(top5, getOutput('top5'))

if __name__ == "__main__":
    print("Choose a path to the fixtures.json")
    folder = getOutputFolder('parsedFixture')
    path = f"{folder}{selectFileFromPath(folder)}"
    print("Choose a path to the tags.json")
    folderTags = getOutputFolder('helper')
    tagPath = f"{folderTags}{selectFileFromPath(folderTags)}"
    try:
        main(path, tagPath)
    except Exception as e:
        print(e)
        signalHandler(None, None)