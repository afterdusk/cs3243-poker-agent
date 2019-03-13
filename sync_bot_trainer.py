import csv
import random
from test_arena import trainBots

# SERVER SIDE

MASTERFILE = "Agent_Leaderboard"

#================================
#   File related functions
#================================

# References the folder and file extension
def folderize(filename):
    return os.getcwd()+"/player-seeds/" + filename + ".csv"

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
                print(row)
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

def removeAgent(agentName):
    #Removes the agent from the table and DELETES the csv file
    table = []
    with open(folderize(MASTERFILE), mode='r') as readFile:
        csvReader = csv.reader(readFile,  delimiter= ',')
        for currRow in csvReader:
            if currRow[0] == agentName:
                continue
            table.append(currRow)
    readFile.close()

    #Deletes the file
    os.remove(folderize(agentName))

    with open(folderize(MASTERFILE), mode='w') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows(table)
    writeFile.close()

def addAgentToBoard(agentName, weights):
    # Initialize win/loss/performace to 0,0,0
    newAgentRow = [agentName, 0, 0, 0]

    with open(folderize(MASTERFILE), mode='a') as boardFile:
        writer = csv.writer(boardFile)
        writer.writerow(newAgentRow)

def editAgentsOnBoard(winAgent, loseAgent):
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
            if row[0] == winAgent.filename:
                winLine = [line, row]
            if row[0] == loseAgent.filename:
                loseLine = [line,row]
            line += 1
        oldInfo = (winLine,loseLine)
    readFile.close()

    newWinRow = oldInfo[0][1]
    newWinRow[1] = int(newWinRow[1]) + 1
    newWinRow[3] = winAgent.perf
    newLoseRow = oldInfo[1][1]
    newLoseRow[2] = int(newLoseRow[2]) + 1
    newLoseRow[3] = loseAgent.perf
    rows[oldInfo[0][0]] = newWinRow
    rows[oldInfo[1][0]] = newLoseRow
    with open(folderize(MASTERFILE), mode='w') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows(rows)
    writeFile.close()

def getBoard():
    with open(folderize(MASTERFILE), mode='r') as readFile:
        csvReader = csv.reader(readFile, delimiter = ",")
        leaderboard = list(csvReader)
        readFile.close()
        return leaderboard

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
def composeBot(agentName):
    data = readFileAndGetData(agentName)
    agentWeights = data[0]
    agentStats = data[1]
    agentClassName = "MySyncablePlayer"
    return (agentClassName, agentName, agentWeights,agentStats)

def settleMatchOutcome(outcome):
    winnerName = outcome[0]
    loserName = outcome[1]
    winner.reward()
    loser.deward()

def arrangeMatch(bot_1, bot_2, iterations):
    num_games = 4
    num_rounds = 101
    training_regime = (num_games,num_rounds)
    print("\n============Match number " + str(iterations) +"============")
    outcome = trainBots(bot_1, bot_2, training_regime)
    settleMatchOutcome(outcome)

def getRandomBotsFromBoard():
    leaderboard = getBoard()
    #print(leaderboard)
    numberOfBots = len(leaderboard) - 1
    first = random.randint(1,numberOfBots)
    second = random.randint(1,numberOfBots)
    while second == first:
        second = random.randint(1,numberOfBots)
    return (leaderboard[first][0],leaderboard[second][0])

def beginTrainingAllBots(cycles):
    iterations = 0
    while iterations < cycles:
        bots = getRandomBotsFromBoard()
        arrangeMatch(bots[0], bots[1], iterations)
        iterations += 1

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
        deadbot = arrangeMatch(botName,opponent, iterations)
        if len(deadbot) > 1:
            return False
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
        alive = trainNamedBot(bot)
        if not alive:
            break
        line += 1

# MAIN

# clearAllHistories()
# beginTrainingAllBots(1500)
# i = 0
# while i < 50:
#     roundRobinTraining()
#     print("/n/n%%%%%%%%%%%%%%%%%%%%%% Finished Round Robin round " + str(i+1) +"%%%%%%%%%%%%%%%%%%%%%%/n/n")
#     i += 1
