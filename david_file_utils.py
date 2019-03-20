import csv
import os
import random

MASTERFILE = "Agent_Leaderboard"
FOLDER_NAME = "agentboards"

def getStats(name, board):
    return board[name][0]

def getWeights(name, board):
    return board[name][1]

def writeStats(name, board, win = 0, lose = 0, perf = 0):
    stats = getStats(name,board)
    board[name][0] = (stats[0] + win, stats[1] + lose, stats[2] + perf)

def overwriteStats(name, board, stats):
    board[name][0] = stats

def overwriteWeights(name, board, weights):
    board[name][1] = weights

def cacheLeaderboard(boardFileName):
    rawLeaderboard = getLeaderboard(boardFileName)
    leaderboard = {}
    for row in rawLeaderboard[2:]:
        name = row[0]
        scores = tuple(map(lambda e: float(e), row[1:4])) #Last not inclusive
        weights = list(map(lambda e: float(e), row[5:]))
        leaderboard[name] = [scores, weights]
    return leaderboard


def writeToLeaderboardFile(leaderboard, generation, boardFilename):
    HEADER = ('Agent Name', 'Wins', 'Losses','Performance')
    GENERATIONS = ('Generation:', generation)
    fileContent = [HEADER,GENERATIONS]
    for agentName in leaderboard:
        stats = leaderboard[agentName][0]
        weights = leaderboard[agentName][1]
        row = (agentName, stats[0], stats[1],stats[2], "Weights:") + tuple(weights)
        fileContent.append(row)

    with open(folderize(boardFilename), mode='w') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows(fileContent)
    writeFile.close()

def writeToFile(filename, *data):
    contentToWrite = data[0]
    with open(folderize(filename), mode='w') as outputFile:
        myWriter = csv.writer(outputFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in contentToWrite:
            # Debug print for raw info read from csv file
            #print("Row: ", row)
            myWriter.writerow(row)
        outputFile.close()

def readFileAndGetData(filename):
    with open(folderize(filename)) as csvFile:
        csvReader = csv.reader(csvFile, delimiter= ',')
        line = 0
        data = []
        for row in csvReader:
            parsedRow = []
            if line == 0:
                for e in row:
                    if len(e) > 0:
                        parsedRow.append(float(e))
                    else:
                        parsedRow.append(e)
                data.append(parsedRow)
            else:
                data.append(row)
            line += 1
        #print('\nProcessed '+ str(line) +' lines\n')
        csvFile.close()
        return data

# Returns the leaderboard
def getLeaderboard(filename):
    with open(folderize(filename), mode='r') as readFile:
        csvReader = csv.reader(readFile, delimiter = ",")
        leaderboard = list(csvReader)
    readFile.close()
    return leaderboard

# References the folder and file extension
def folderize(filename):
#    return os.getcwd()+ "/" + filename + ".csv"
    return os.getcwd()+"/" + FOLDER_NAME +"/" + filename + ".csv"
