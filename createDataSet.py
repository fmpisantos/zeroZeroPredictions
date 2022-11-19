# Path: createDataSet.py
import json
import sys
import config
import utils
from multiprocessing import Pool

# Output:
# [
#   {
#       fixture: [fixtureId, homeTeam, day, awayTeam, ...],
#       statistics: [[homeTeamStatistics], [awayTeamStatistics]],
#       predictions: [footballApiPrediction]
#   }
# ]

# Get fixtures for a day
def getFixturesForDay(date):
    # Get fixtures for a day
    return utils._request(f"v3/fixtures?date={date}", filename={date})

# Get fixture predictions
def getFixturePredictions(fixture):
   return utils._request(f"v3/predictions?fixture={fixture}", filename={fixture})

def getFixturesStatisticsAndPredictionsParallel(fixture):
    # Get fixture statistics
    # homeTeamStatistics = utils.getTeamStatistics(fixture['teams']['home']['id'], fixture['league']['id'], fixture['league']['season'], utils.getPreviousDay(fixture['fixture']['date'].split('T')[0]))
    # awayTeamStatistics = utils.getTeamStatistics(fixture['teams']['away']['id'], fixture['league']['id'], fixture['league']['season'], utils.getPreviousDay(fixture['fixture']['date'].split('T')[0]))
    # Get fixture predictions
    fixturePredictions = getFixturePredictions(fixture['fixture']['id'])
    sys.stdout.write(f"\r                                                                                                                       ")
    sys.stdout.flush()
    sys.stdout.write(f"\r({fixture['fixture']['id']} - {fixture['teams']['home']['name']} vs {fixture['teams']['away']['name']})")
    sys.stdout.flush()
    # Add statistics and predictions to fixture
    # fixture['statistics'] = [homeTeamStatistics, awayTeamStatistics]
    fixture['predictions'][0] = fixturePredictions
    return fixture

# Loop through all fixtures and get statistics and predictions
def getFixturesStatisticsAndPredictions(fixtures, requests):
    # Loop through all fixtures and get statistics and predictions
    for fixture in fixtures:
        # Get fixture statistics
        # homeTeamStatistics = utils.getTeamStatistics(fixture['teams']['home']['id'], fixture['league']['id'], fixture['league']['season'], utils.getPreviousDay(fixture['fixture']['date'].split('T')[0]))
        # awayTeamStatistics = utils.getTeamStatistics(fixture['teams']['away']['id'], fixture['league']['id'], fixture['league']['season'], utils.getPreviousDay(fixture['fixture']['date'].split('T')[0]))
        # Get fixture predictions
        fixturePredictions = getFixturePredictions(fixture['fixture']['id'])
        requests += 1
        sys.stdout.write(f"\rRequest {requests} ({fixture['fixture']['id']} - {fixture['teams']['home']['name']} vs {fixture['teams']['away']['name']})")
        sys.stdout.flush()
        # Add statistics and predictions to fixture
        # fixture['statistics'] = [homeTeamStatistics, awayTeamStatistics]
        fixture['predictions'][0] = fixturePredictions
    return fixtures

# Get fixtures from a day backwards until hit requestsPerDay
def getFixturesFromDayBackwards(date, nRequests = 0):
    # Get fixtures from a day backwards until hit requestsPerDay
    fixtures = []
    fixturesForDay = None
    while nRequests < config.requestsPerDay:
        nRequests += len(fixturesForDay) if fixturesForDay != None else 0
        if nRequests >= config.requestsPerDay:
            break
        print(f"Requests so far: {nRequests}")
        # Get fixtures for a day
        print(f"fixturesForDay({date})")
        fixturesForDay = getFixturesForDay(date)
        nRequests += 1
        # If no fixtures for a day, break
        if (fixturesForDay != None and len(fixturesForDay) == 0) or fixturesForDay == None:
            # Get previous day
            date = utils.getPreviousDay(date)
            continue
        # Get statistics and predictions for all fixtures
        with Pool(5) as p:
            fixturesForDay = p.map(getFixturesStatisticsAndPredictionsParallel, fixturesForDay)
        print("\n")
        # fixturesForDay = getFixturesStatisticsAndPredictions(fixturesForDay, nRequests)
        # Add fixtures for a day to fixtures
        fixtures.extend(fixturesForDay)
        # Get previous day
        date = utils.getPreviousDay(date)
    utils.writeToFile(nRequests,config.getNRequestsPath(), type="w")
    return fixtures

def fromStringPercentToFloat(percent):
    try:
        return float(percent.split('%')[0]) / 100
    except:
        return 0.0

def parseFixtureAverage(game):
    keys = list(game.keys()).copy()
    for key in keys:
        if 'homeTeam.' in key:
            newKey = key.replace('homeTeam.', 'averageTeam.')
            awayKey = key.replace('homeTeam.', 'awayTeam.')
            if(awayKey in game):
                game[newKey] = (game[key] + game[awayKey]) / 2
    return game

# Parse fixture to game format
def parseFixture(game, fixture, type):
    total = int(fixture['predictions'][0]['teams'][type]['league']['fixtures']['played']['total'])
    game[f'{type}Team.total'] = total
    if(total == 0):
        return game
    game[f'{type}Team.form'] = fromStringPercentToFloat(fixture['predictions'][0]['teams'][type]['last_5']['form'])
    game[f'{type}Team.att'] = fromStringPercentToFloat(fixture['predictions'][0]['teams'][type]['last_5']['att'])
    game[f'{type}Team.def'] = fromStringPercentToFloat(fixture['predictions'][0]['teams'][type]['last_5']['def'])
    game[f'{type}Team.goals'] = float(fixture['predictions'][0]['teams'][type]['last_5']['goals']['for']['average']) + float(fixture['predictions'][0]['teams'][type]['last_5']['goals']['against']['average'])
    if total:
        game[f'{type}Team.league.fixtures.notDrawPrediction'] = int(fixture['predictions'][0]['teams'][type]['league']['fixtures']['draws']['total']) / total
    game[f'{type}Team.league.goals.average'] = float(fixture['predictions'][0]['teams'][type]['league']['goals']['for']['average'][type]) + float(fixture['predictions'][0]['teams'][type]['league']['goals']['against']['average'][type])
    averageGoalsPer15MinPeriod = [fromStringPercentToFloat(fixture['predictions'][0]['teams'][type]['league']['goals']['for']['minute'][f"{i*15+(1 if i != 0 else 0)}-{i*15+15}"]['percentage']) for i in range(0, 6)]
    averageGoalsPer15MinPeriod += [fromStringPercentToFloat(fixture['predictions'][0]['teams'][type]['league']['goals']['against']['minute'][f"{i*15+(1 if i != 0 else 0)}-{i*15+15}"]['percentage']) for i in range(0, 6)]
    averageGoalsPer15MinPeriod = list(filter(lambda x: x > 0, averageGoalsPer15MinPeriod))
    if(len(averageGoalsPer15MinPeriod) > 0):
        game[f'{type}Team.league.minutePercentAverage'] = sum(averageGoalsPer15MinPeriod)/len(averageGoalsPer15MinPeriod)
    if total:
        game[f'{type}Team.notClearSheets'] = int(fixture['predictions'][0]['teams'][type]['league']['clean_sheet']['total']) / total
    if total:
        game[f'{type}Team.notFailedToScore'] = int(fixture['predictions'][0]['teams'][type]['league']['failed_to_score']['total']) / total
    return game

# Parse fixtures to game format
def parseFixtures(fixtures, path):
    # Parse fixtures to game format
    games = []
    for i, fixture in enumerate(fixtures):
        game = {}
        game['id'] = i
        game['filepath'] = path
        game['fixture'] = fixture['fixture']['id']
        try:
            game['green'] = int(fixture['goals']['home']) + int(fixture['goals']['away']) != 0
        except:
            continue
        if fixture['predictions'] == None:
            continue
        game['notDrawPrediction'] = 1 - int(fixture['predictions'][0]['predictions']['percent']['draw'].split('%')[0]) / 100 
        game = parseFixture(game, fixture, 'home')
        game = parseFixture(game, fixture, 'away')
        game = parseFixtureAverage(game)
        game['comparison.form'] = fromStringPercentToFloat(fixture['predictions'][0]['comparison']['form']['home']) + fromStringPercentToFloat(fixture['predictions'][0]['comparison']['form']['away']) * 0.5
        game['comparison.att'] = fromStringPercentToFloat(fixture['predictions'][0]['comparison']['att']['home']) + fromStringPercentToFloat(fixture['predictions'][0]['comparison']['att']['away']) * 0.5
        game['comparison.def'] = fromStringPercentToFloat(fixture['predictions'][0]['comparison']['def']['home']) + fromStringPercentToFloat(fixture['predictions'][0]['comparison']['def']['away']) * 0.5
        game['comparison.poisson_distribution'] = fromStringPercentToFloat(fixture['predictions'][0]['comparison']['poisson_distribution']['home']) + fromStringPercentToFloat(fixture['predictions'][0]['comparison']['poisson_distribution']['away']) * 0.5
        game['comparison.h2h'] = fromStringPercentToFloat(fixture['predictions'][0]['comparison']['h2h']['home']) - fromStringPercentToFloat(fixture['predictions'][0]['comparison']['h2h']['away']) * 0.5
        game['comparison.goals'] = fromStringPercentToFloat(fixture['predictions'][0]['comparison']['goals']['home']) + fromStringPercentToFloat(fixture['predictions'][0]['comparison']['goals']['away']) * 0.5
        game['comparison.total'] = fromStringPercentToFloat(fixture['predictions'][0]['comparison']['total']['home']) + fromStringPercentToFloat(fixture['predictions'][0]['comparison']['total']['away']) * 0.5
        games.append(game)
    return games

# Read fixture file and parse fixtures
def readFixtureFile(path):
    with open(path) as file:
        fixtures = json.load(file)
        games = parseFixtures(fixtures, path)
        utils.writeToFile(games, config.getOutput('parsedFixture', utils.getFileNameFromPath(path, withExtension = False)), type="w")

# Get Fixture and stats from API
def getFixturesFromAPI():
    # Load number of requests done today
    try :
        nRequests = utils.readIntFromFile(config.getNRequestsPath())
    except Exception as e:
        nRequests = 0
    # Get yesterday date
    date = utils.getPreviousDay()
    # Get fixtures from a day backwards until hit requestsPerDay
    fixtures = getFixturesFromDayBackwards(date, nRequests)
    # Write fixtures to file
    utils.writeToFile(fixtures, config.getOutput('fixtures'), type="w")

# Main
if __name__ == "__main__":
    folder = config.getOutputFolder('fixtures')
    readFixtureFile(f"{folder}{utils.selectFileFromPath(folder)}")
