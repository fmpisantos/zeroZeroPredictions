from datetime import datetime

# Constants
GET = "GET"
POST = "POST"
PUT = "PUT"
url = "https://api-football-v1.p.rapidapi.com"
headers = {
    'X-RapidAPI-Key': 'f4a08b08f8mshe62281c6ac04ff4p113284jsncbc6e324673c',
    'X-RapidAPI-Host': 'api-football-v1.p.rapidapi.com'
    }
output = "output/"
errorsOutput = "errors/"
printToConsole = False
dbLocation = "output/clearedData/db.json"

maxNumberOfDailyRequests = 75000
requestsPerDay = 2000

# Variables
now = datetime.now()

# Functions
def getOutput(request = "", filename=""):
    return f"{output}/{f'{request}/' if len(request) > 0 else ''}{filename if len(filename) > 0 else now.today().strftime('%Y-%m-%d(%H:%M)')}.json"

def getErrorOutput(request = "", filename=""):
    return f"{errorsOutput}{f'{request}/' if len(request) > 0 else ''}{filename if len(filename) > 0 else now.today().strftime('%Y-%m-%d(%H:%M)')}.json"

def getUrl(request = ""):
    return f"{url}/{request}"

def getNRequestsPath():
    return f"{output}/nRequests.json"