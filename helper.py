import utils
import config

def main(path):
    fixtures = utils.loadFromDB(path)
    if fixtures is None:
        return None
    utils.writeToFile(list(fixtures[0].keys()), config.getOutput('helper', 'bruteForce.json'))

if __name__ == "__main__":
    folder = config.getOutputFolder('parsedFixture')
    main(f"{folder}{utils.selectFileFromPath(folder)}")