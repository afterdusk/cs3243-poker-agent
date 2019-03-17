import csv
import os
import random
from collections import deque
from CLIENT_stadium import train_bots
from SERVER_incubator import incubate
from david_file_utils import folderize, readFileAndGetData, writeToFile, getLeaderboard, MASTERFILE

# SERVER SIDE david_player trainer
rawLeaderboard = getLeaderboard(MASTERFILE)

LEADERBOARD = {}
for row in rawLeaderboard[1:]:
    name = row[0]
    scores = tuple(map(lambda e: float(e), row[1:]))
    LEADERBOARD[name] = scores

def writeToLeaderboardFile():
    HEADER = ('Agent Name', 'Wins', 'Losses','Performance')
    fileContent = [HEADER,]
    for agentName in LEADERBOARD:
        stats = LEADERBOARD[agentName]
        row = (agentName, stats[0], stats[1],stats[2])
        fileContent.append(row)

    with open(folderize(MASTERFILE), mode='w') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows(fileContent)
    writeFile.close()

#================================
#   File related functions
#================================
def updateAgentsLeaderboardStats(winAgentName, loseAgentName):
    #updates the LEADERBOARD
    stats = LEADERBOARD[winAgentName]
    LEADERBOARD[winAgentName] = (stats[0] + 1, stats[1], stats[2])

    lstats = LEADERBOARD[loseAgentName]
    LEADERBOARD[winAgentName] = (lstats[0], lstats[1] + 1, lstats[2])

#================================
#   Training related functions
#================================
def getRandomBotsFromBoard():
    botNameList = list(LEADERBOARD.keys())
    #print(leaderboard)
    first = random.choice(botNameList)
    second = random.choice(botNameList)
    while second == first:
        second = random.choic(botNameList)
    return (first,second)

def beginTrainingAllBots(cycles):
    iterations = 0
    while iterations < cycles:
        bots = getRandomBotsFromBoard()
        arrangeMatch(bots[0], bots[1])
        iterations += 1

def trainNamedBot(botName):
    board = LEADERBOARD
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

        oppIndex += 1
        if oppIndex >= len(board):
            break
        iterations += 1
    return True

def roundRobinTraining():
    print("ROUND ROBIN TRAINING")
    board = LEADERBOARD
    botlist = []
    for row in board[0:]:
        botlist.append(row[0])
    line = 0
    for bot in botlist:
        if line == 0:
            line += 1
            continue
        trainNamedBot(bot)

        # TODO need to check if the bot being trained is still alive
        alive = 1
        if not alive:
            break
        line += 1

def settleMatchOutcome(outcome):
    winnerName = outcome[0]
    loserName = outcome[1]
    updateAgentsLeaderboardStats(winnerName,loserName)

#************================================************
#         Server-Client communication functions
#************================================************

def composeBot(agentName):
    data = readFileAndGetData(agentName)
    agentWeights = data[0]
    agentStats = data[1]
    agentClassName = "DavidPlayer"
    return (agentClassName, agentWeights)

# TODO: Move this to somewhere less awkward
matchup_queue = deque()

# Sends a message to the clients in the form of a tuple
# matchup_job = ((bot_1, bot_2), training_configuration, (b1Name, b2Name))
def sendMatchup(matchup_job):
    print(matchup_job)
    outcome = train_bots(matchup_job)
    handleOutcome(outcome)
    #schedule_job(matchup_job, 120, handleOutcome)

INCUBATEFREQUENCY = len(LEADERBOARD)
matchCount = 1
stabilizer = 197

# Processes outcomes received from remote clients
# Message contains a tuple of (winner_name,loser_name)
def handleOutcome(outcome):
    global matchCount
    # global INCUBATEFREQUENCY
    print("\n============Match number " + str(matchCount) +"============")
    settleMatchOutcome(outcome)
    matchCount += 1
    # if matchCount > stabilizer:
    #     if matchCount % INCUBATEFREQUENCY == 0 and matchCount >= INCUBATEFREQUENCY:
    #         incubate(LEADERBOARD)

# Composes the bots based on bot names
def arrangeMatch(agentOneName, agentTwoName):
    botOne = composeBot(agentOneName)
    botTwo = composeBot(agentTwoName)
    num_games = 5
    num_rounds = 101
    training_regime = (num_games,num_rounds)
    # ((b1,b2), (ng,nr), (name1,name2))
    matchup_job = ((botOne, botTwo),training_regime,(agentOneName,agentTwoName))
    sendMatchup(matchup_job)

def getNextMatch():
    try:
        return matchup_queue.popleft()
    except Exception as e:
        print("Got error getting next job", e)
        return None

def init(taskmaster):
    # This is the main training
    TASKMASTER = taskmaster
    try:
        beginTrainingAllBots(300)
    except Exception as e:
        print(e)
        writeToLeaderboardFile()

# MAIN
if __name__ == "__main__":
    beginTrainingAllBots(300)

#    init("blae")
    # i = 0
    # while i < 50:
    #     roundRobinTraining()
    #     print("/n/n%%%%%%%%%%%%%%%%%%%%%% Finished Round Robin round " + str(i+1) +"%%%%%%%%%%%%%%%%%%%%%%/n/n")
    #     i += 1
