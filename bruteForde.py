import sys
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

def calculateBruteForce(fixtures = [], tags = []):
    if len(fixtures) == 0 or len(tags) == 0:
        return None
    greenGames = 0
    for fixture in fixtures:
        predictedGreen = True
        for tag in tags:
            if tag['tag'] in fixture:
                home = tag['tag'].replace("averageTeam.", "homeTeam.")
                away = tag['tag'].replace("averageTeam.", "awayTeam.")
                if "Team" in tag['tag']:
                    if function(tag['tag'], tag['min'], fixture[home], fixture[away],fixture[tag['tag']]) == False:
                        predictedGreen = False
                        break
                else:
                    if function(tag['tag'], tag['min'], None, None,fixture[tag['tag']]) == False:
                        predictedGreen = False
                        break
        if predictedGreen:
            if fixture['green']:
                greenGames += 1
            else:
                redGames += 1
    return greenGames, len(fixtures)

# calculate increment for a tag
def getIncrement(tag):
    inc = 0.1 if "increment" not in tag else tag["increment"]
    if tag['tag'] in smallestTheBest or tag['tag'] in singleSmallest:
        return inc * -1
    return inc

def checkIfGreensBiggerThanAnyOther(result, results):
    if len(results) < 5:
        results += [result]
        return
    for r in results:
        if r["greens"] > result["greens"]:
            r = result

def incrementTag(tags, idx):
    if idx == -1 or idx > len(tags) - 1:
        return False
    tag = tags[idx]
    tag["min"] += tag["inc"]
    if ( tag["inc"] > 0 and tag["min"] >= tag["max"] ) or ( tag["inc"] < 0 and tag["min"] <= tag["max"] ):
        tag[idx]["min"] = 0
        incrementTag(tags, idx + 1)
    return True

# create a loop that iterates over all the tags with all combinations and all min and max values and calls calculateBruteForce
def loopTags(tags, fixtures, maxIterations = 0):
    top5 = []
    results = []
    itNum = 0
    while True:
        itNum += 1
        print(f"{itNum}/{maxIterations}")
        if not incrementTag(tags, 0):
            break
        # call calculateBruteForce
        greens, total = calculateBruteForce(fixtures, tags)
        # replace top 5 if needed
        result = {"greens": greens, "reds": total - greens, "percent" : greens / total, "tags": tags}
        checkIfGreensBiggerThanAnyOther(result, top5)
        # save results
        results += result
    return results, top5

def getNumberOfIterations(tags):
    iterations = 1
    for tag in tags:
        iterations *= (tag["max"] - tag["min"]) / tag["inc"]
    return iterations

def main(path):
    fixtures = loadFromDB(path)
    if fixtures is None:
        return None
    fixtures = [f for f in fixtures if f['homeTeam.total'] + f['awayTeam.total'] > minNumberOfGames]
    tags = loadFromDB(f"{getOutputFolder('helper')}bruteForce.json")
    tags = [{"tag": tag['tag'], "max": tag['max'], "inc": getIncrement(tag), "min": 0} for tag in tags]
    results, top5 = loopTags(tags, fixtures, getNumberOfIterations(tags))
    writeToFile(results, getOutput('results'))
    writeToFile(top5, getOutput('top5'))

if __name__ == "__main__":
    folder = getOutputFolder('parsedFixture')
    main(f"{folder}{selectFileFromPath(folder)}")