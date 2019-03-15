import csv
import os
import random
from CLIENT_test_arena import train_bots
from SERVER_incubator import incubate
from file_utils import folderize, readFileAndGetData, writeToFile, getLeaderboard

# SERVER SIDE bot match taskmaster

MASTERFILE = "Agent_Leaderboard"

getBoard = lambda : getLeaderboard(MASTERFILE)

#================================
#   File related functions
#================================
def updateAgentsLeaderboardStats(winAgentName, loseAgentName):
    #updates the Agent_Leaderboard
    oldInfo = []
    with open(folderize(MASTERFILE)) as readFile:
        csvReader = csv.reader(readFile,  delimiter= ',')
        rows = list(csvReader)
    readFile.close()

    with open(folderize(MASTERFILE)) as readFile:
        csvReader = csv.reader(readFile,  delimiter= ',')
        line = 0
        winLine = 0
        loseLine = 0
        for row in csvReader:
            if row[0] == winAgentName:
                winLine = [line, row]
            if row[0] == loseAgentName:
                loseLine = [line,row]
            line += 1
        oldInfo = (winLine,loseLine)
    readFile.close()

    newWinRow = oldInfo[0][1]
    newWinRow[1] = int(newWinRow[1]) + 1 # Increment wins
    newWinRow[3] = int(newWinRow[3]) + 1 # Increment performance
    newLoseRow = oldInfo[1][1]
    newLoseRow[2] = int(newLoseRow[2]) + 1 # Increment losses
    newLoseRow[3] = int(newLoseRow[3]) - 1  # Decrease performance
    rows[oldInfo[0][0]] = newWinRow
    rows[oldInfo[1][0]] = newLoseRow
    with open(folderize(MASTERFILE), mode='w') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows(rows)
    writeFile.close()


def clearAllHistories():
    # Sets all local win-loss-performace histories of bots to 0,0,0
    # Does not affect the leaderboard
    board = getBoard()
    boardLine = 0
    for row in board:
        if boardLine == 0:
            boardLine = 1
            continue
        target = row[0]
        with open(folderize(target)) as readFile:
            csvReader = csv.reader(readFile,  delimiter= ',')
            line = 0
            newContents = []
            for row in csvReader:
                if line == 1:
                    newContents.append((0,0,0))
                else:
                    newContents.append(row)
                line += 1
        readFile.close()

        with open(folderize(target), mode='w') as writeFile:
            writer = csv.writer(writeFile)
            writer.writerows(newContents)
        writeFile.close()

#================================
#   Training related functions
#================================
def getRandomBotsFromBoard():
    leaderboard = getBoard()
    #print(leaderboard)
    numberOfBots = len(leaderboard) - 1
    first = random.randint(1,numberOfBots)
    second = random.randint(1,numberOfBots)
    while second == first:
        second = random.randint(1,numberOfBots)
    return (leaderboard[first][0],leaderboard[second][0])

def beginTrainingAllBots(cycles, incubateFrequency):
    iterations = 0
    while iterations < cycles:
        bots = getRandomBotsFromBoard()
        arrangeMatch(bots[0], bots[1], iterations)
        iterations += 1
        if iterations % incubateFrequency == 0:
            incubate(getBoard())

def trainNamedBot(botName):
    board = getBoard()
    iterations = 0
    oppIndex = 1
    for row in board:
        opponent = board[oppIndex][0]
        if opponent == botName:
            oppIndex += 1
            if oppIndex < len(board):
                opponent = board[oppIndex][0]
            else:
                break
        arrangeMatch(botName,opponent, iterations)

        # TODO need to return if the bot being trained is still alive

        oppIndex += 1
        if oppIndex >= len(board):
            break
        iterations += 1
    return True

def roundRobinTraining():
    print("ROUND ROBIN TRAINING")
    board = getBoard()
    botlist = []
    for row in board[0:]:
        botlist.append(row[0])
    line = 0
    for bot in botlist:
        if line == 0:
            line += 1
            continue
        trainNamedBot(bot)
        incubate(getBoard())

        # TODO need to check if the bot being trained is still alive
        alive = 1
        if not alive:
            break
        line += 1

def reward(winnerName):
    # Open winnerName file
    data = readFileAndGetData(winnerName)
    newStats = data[1]
    newStats[0] = int(newStats[0]) + 1 #Increment wins
    newStats[2] = int(newStats[2]) + 1 #Increment performance
    # Update the csv
    writeToFile(winnerName,[data[0],newStats])

def penalize(loserName):
    # Open loserName file
    data = readFileAndGetData(loserName)
    newStats = data[1]
    newStats[1] = int(newStats[1]) + 1 #Increment losses
    newStats[2] = int(newStats[2]) - 1 #Decrease performance
    # Update the csv
    writeToFile(loserName,[data[0],newStats])

def settleMatchOutcome(outcome):
    winnerName = outcome[0]
    loserName = outcome[1]
    reward(winnerName)
    penalize(loserName)
    updateAgentsLeaderboardStats(winnerName,loserName)

#************================================************
#         Server-Client communication functions
#************================================************

def composeBot(agentName):
    data = readFileAndGetData(agentName)
    agentWeights = data[0]
    agentStats = data[1]
    agentClassName = "MySyncablePlayer"
    return (agentClassName, agentName, agentWeights,agentStats)

# Sends a message to the clients in the form of a tuple
# matchup_job = ((bot_1, bot_2), training_configuration)
def sendMatchup(matchup_job):
    # E-Liang help pls

    # Testing
    result = train_bots(matchup_job)
    settleMatchOutcome(result)
    pass

# Recieves from Clients
# Message contains a tuple of (winner_name,loser_name)
def recieveOutcome(port_or_something):
    # E-Liang help pls
    settleMatchOutcome(outcome)

def arrangeMatch(agentOneName, agentTwoName, iterations):
    botOne = composeBot(agentOneName)
    botTwo = composeBot(agentTwoName)
    num_games = 5
    num_rounds = 101
    training_regime = (num_games,num_rounds)
    print("\n============Match number " + str(iterations) +"============")
    matchup_job = ((botOne, botTwo),training_regime)
    sendMatchup(matchup_job)



# MAIN
clearAllHistories()
beginTrainingAllBots(200,10)
# i = 0
# while i < 50:
#     roundRobinTraining()
#     print("/n/n%%%%%%%%%%%%%%%%%%%%%% Finished Round Robin round " + str(i+1) +"%%%%%%%%%%%%%%%%%%%%%%/n/n")
#     i += 1