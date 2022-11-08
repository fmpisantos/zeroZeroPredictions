# Path: createDataSet.py
import config
import utils

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
    return utils._request(f"v3/fixtures?date={date}")

# Get fixture predictions
def getFixturePredictions(fixture):
   return utils._request(f"v3/fixtures/predictions?fixture={fixture}")

# Loop through all fixtures and get statistics and predictions
def getFixturesStatisticsAndPredictions(fixtures):
    # Loop through all fixtures and get statistics and predictions
    for fixture in fixtures:
        # Get fixture statistics
        homeTeamStatistics = utils.getTeamStatistics(fixture['teams']['home']['id'], fixture['league']['id'], fixture['league']['season'], utils.getPreviousDay(fixture['fixture']['date'].split('T')[0]))
        awayTeamStatistics = utils.getTeamStatistics(fixture['teams']['away']['id'], fixture['league']['id'], fixture['league']['season'], utils.getPreviousDay(fixture['fixture']['date'].split('T')[0]))
        # Get fixture predictions
        fixturePredictions = getFixturePredictions(fixture['fixture']['id'])
        # Add statistics and predictions to fixture
        fixture['statistics'] = [homeTeamStatistics, awayTeamStatistics]
        fixture['predictions'] = fixturePredictions
    return fixtures

# Get fixtures from a day backwards until hit requestsPerDay
def getFixturesFromDayBackwards(date, nRequests = 0):
    # Get fixtures from a day backwards until hit requestsPerDay
    fixtures = []
    while nRequests < config.requestsPerDay:
        # Get fixtures for a day
        fixturesForDay = getFixturesForDay(date)
        nRequests += 1
        # If no fixtures for a day, break
        if fixturesForDay != None and len(fixturesForDay) == 0:
            break
        # Get statistics and predictions for all fixtures
        fixturesForDay = getFixturesStatisticsAndPredictions(fixturesForDay)
        nRequests += 3 * (fixturesForDay != None and len(fixturesForDay) or 0)
        # Add fixtures for a day to fixtures
        fixtures.extend(fixturesForDay)
        # Get previous day
        date = utils.getPreviousDay(date)
    utils.writeToFile(nRequests,config.getOutput('requests'))
    return fixtures


# Main
if __name__ == "__main__":
    # Load number of requests done today
    try : 
        nRequests = utils.readJsonFile(config.getOutput('requests'))
    except:
        nRequests = 0
    # Get yesterday date
    date = utils.getPreviousDay()
    # Get fixtures from a day backwards until hit requestsPerDay
    fixtures = getFixturesFromDayBackwards(date, nRequests)
    # Write fixtures to file
    utils.writeToFile(fixtures, config.getOutput('fixtures'))