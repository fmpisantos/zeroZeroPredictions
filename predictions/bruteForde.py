import sys
import config
import utils

# create class Tag with tag, min and max attributes
class Tag:
  def __init__(self, tag, min, max):
    self.tag = tag
    self.min = min
    self.max = max

def function(tagValue, min = None):
    return tagValue >= (min if min is not None else 0) and tagValue <= (max if max is not None else sys.maxint)

def calculateBruteForce(fixtures = [], tags = []):
    if len(fixtures) == 0 or len(tags) == 0:
        return None
    greenGames = 0
    redGames = 0
    for fixture in fixtures:
        predictedGreen = True
        for tag in tags:
            if tag.tag in fixture:
                if function(fixture[tag.tag], tag.min, tag.max) == False:
                    predictedGreen = False
                    break
        if predictedGreen:
            if fixture['green']:
                greenGames += 1
            else:
                redGames += 1
    return greenGames, len(fixtures)

def main(path):
    fixtures = utils.loadFromDB(path)
    if fixtures is None:
        return None
    fixtures = [f for f in fixtures if f['homeTeamGoals'] + f['awayTeamGoals'] > config.minNumberOfGoals]
    # create a loop that iterates over all the tags with all combinations and all min and max values
    # and then call calculateBruteForce with the tags and fixtures
    # and then print the results
    # and then save the results to a file
    # tags format: [Tag(tag = 'homeTeamGoals', min = 0, max = 1), Tag(tag = 'awayTeamGoals', min = 0, max = 1)]


if __name__ == "__main__":
    folder = config.getOutputFolder('parsecFixture')
    main(f"{folder}{utils.selectFileFromPath(folder)}")