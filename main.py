import utils
import config

db = utils.loadFromDB("output/clearedData/2022-11-06(18:02).json")
# db = utils.loadFromDB()

def getStatsHelper(team, teamID, leagueID, season, date, string):
    teamStats = utils.getTeamStatistics(teamID, leagueID, season, date)
    if teamStats != None:
        teamStats.pop('league', None)
        teamStats.pop('team', None)
        team[string] = teamStats
        return team
    else:
        raise Exception("Error in getStatsHelper")

# get teamStatistics for every team in db and append to db
def getTeamStatistics():
    for team in (item for item in db if (not utils.hasKey(item, "Team1Stats") or not utils.hasKey(item, "Team2Stats")) and utils.hasKey(item, "Team1Id") and utils.hasKey(item, "Team2Id")):
        try:
            team = getStatsHelper(team, team['Team1Id'], team['LeagueId'], team['Season'], team['Date'].split('T')[0],"Team1Stats")
            team = getStatsHelper(team, team['Team2Id'], team['LeagueId'], team['Season'], team['Date'].split('T')[0], "Team2Stats")
        except:
            print("Error in getTeamStatistics")
            break
    utils.writeToFile(db, config.getOutput("clearedData"))

# count how many items in db have Team1Stats and Team2Stats (return itemsWithStats, itemsWithoutStats)
def countStats():
    itemsWithStats = len([item for item in db if  not utils.hasKey(item, "Team1Stats") and not utils.hasKey(item, "Team2Stats") and utils.hasKey(item, "Team1Id") and utils.hasKey(item, "Team2Id")])
    return itemsWithStats, abs(len(db) - itemsWithStats)

def testStats():
    return utils.getTeamStatistics(3704, 344, 2020, "2020-12-16")

# count teams with out Team1ID and Team2ID
def unidentifiedTeams():
    temp = [item for item in db if not utils.hasKey(item, "Team1Id") and not utils.hasKey(item, "Team2Id")]
    return temp

def main():
    # getTeamStatistics()
    # print(f"itemsWithStats, itemsWithoutStats : {countStats()}")
    print(len(unidentifiedTeams()))

if __name__ == "__main__":
    main()