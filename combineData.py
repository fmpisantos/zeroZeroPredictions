import utils
import config

# Constants
excelFieldsToKeep = [   
    "Data",
    "Team1", "Team2",
    "OverTeam1", "OverTeam2", 
    "ScoringRateTeam1", "ScoringRateTeam2",
    "H2H",
    "CleanSheetsTeam1", "CleanSheetsTeam2",
    "OVER 1.5 TEAM1", "OVER 1.5 TEAM2",
    "Over2.5Team1", "Over2.5Team2",
    "BothTeamsScoreTeam1", "BothTeamsScoreTeam2",
    "0.5IntervaloTeam1", "0.5IntervaloTeam2",
    "Min 1 Goal",
    "Odd empate"
]

excelFieldsToKeepNewTags = {
    "Data": "Date",
    "H2H": "Head2Head",
    "OVER 1.5 TEAM1": "Over1.5Team1",
    "OVER 1.5 TEAM2": "Over1.5Team2",
    "Min 1 Goal": "Min1Goal",
    "Odd empate": "OddDraw",
    "0.5IntervaloTeam1": "0.5HalfTimeTeam1",
    "0.5IntervaloTeam2": "0.5HalfTimeTeam2"
}

jsonFieldsToKeep = [
    ["fixture","id"],
    ["league","id"],
    ["league","season"],
    ["teams","home","id"],
    ["teams","away","id"],
    ["goals","home"],
    ["goals","away"],
    ["score","halftime","home"],
    ["score","halftime","away"],
    ["score","extratime","home"],
    ["score","extratime","away"],
    ["score","fulltime","home"],
    ["score","fulltime","away"]
]
jsonFieldsToKeepNewTags = {
    "fixture.id": "FixtureId",
    "league.id": "LeagueId",
    "league.season": "Season",
    "teams.home.id": "Team1Id",
    "teams.away.id": "Team2Id",
    "goals.home": "GoalsTeam1",
    "goals.away": "GoalsTeam2",
    "score.halftime.home": "HalfTimeGoalsTeam1",
    "score.halftime.away": "HalfTimeGoalsTeam2",
    "score.extratime.home": "ExtraTimeGoalsTeam1",
    "score.extratime.away": "ExtraTimeGoalsTeam2",
    "score.fulltime.home": "FullTimeGoalsTeam1",
    "score.fulltime.away": "FullTimeGoalsTeam2"
}

# Clear the data
def clearData(data):
    cleanedData = []
    for excelField in data["excel"]:
        temp = {}
        if utils.hasKey(excelField, "Games") and excelField["Games"] != "":
            for field in excelFieldsToKeep:
                if field in excelFieldsToKeepNewTags:
                    temp[excelFieldsToKeepNewTags[field]] = excelField[field]
                elif utils.hasKey(excelField, field):
                    temp[field] = excelField[field]
            # filter array by team1 and team2
            for jsonField in data["json"][excelField["Data"].split("T")[0]]["response"]:
                if utils.stringToUppercase(jsonField["teams"]["home"]["name"]) == data["excelToJson"][utils.stringToUppercase(temp["Team1"])] or utils.stringToUppercase(jsonField["teams"]["away"]["name"]) == data["excelToJson"][utils.stringToUppercase(temp["Team2"])]:
                    for field in jsonFieldsToKeep:
                        if ".".join(field) in jsonFieldsToKeepNewTags:
                            temp[jsonFieldsToKeepNewTags[".".join(field)]] = jsonField
                            for subField in field:
                                temp[jsonFieldsToKeepNewTags[".".join(field)]] = temp[jsonFieldsToKeepNewTags[".".join(field)]][subField]
                        else:
                            temp[".".join(field)] = jsonField
                            for subField in field:
                                temp[".".join(field)] = temp[".".join(field)][subField]
                    cleanedData.append(temp)
                    break
            cleanedData.append(temp)
    return cleanedData

# fill missing Team1Id and Team2Id
def fillMissingTeamIds():
    data = utils.readJsonFile(f"./output/clearedData/db.json")
    values = utils.readJsonFile(f"./assets/values.json")
    for i in range(len(data)):
        if "Team1Id" not in data[i] or "Team2Id" not in data[i]:
            for jsonField in values["json"][data[i]["Date"].split("T")[0]]["response"]:
                if utils.stringToUppercase(jsonField["teams"]["home"]["name"]) == values["excelToJson"][utils.stringToUppercase(data[i]["Team1"])] or utils.stringToUppercase(jsonField["teams"]["away"]["name"]) == values["excelToJson"][utils.stringToUppercase(data[i]["Team2"])]:
                    data[i]["Team1Id"] = jsonField["teams"]["home"]["id"]
                    data[i]["Team2Id"] = jsonField["teams"]["away"]["id"]
                    break
    utils.writeToFile(data, config.getOutput("clearedData"))

# main function
def main():
    # data = {}
    # data = utils.readJsonFile("assets/values.json")
    # cleanedData = clearData(data)
    # utils.writeToFile(cleanedData, config.getOutput("clearedData"))
    fillMissingTeamIds()

if __name__ == "__main__":
    main()