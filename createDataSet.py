# Path: createDataSet.py
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
    fixture['predictions'] = fixturePredictions
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
        fixture['predictions'] = fixturePredictions
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

# Parse fixtures to game format
def parseFixtures(fixtures):
    # Parse fixtures to game format
    games = []
    for fixture in fixtures:
        print(fixture)
    return games

# Main
if __name__ == "__main__":
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
