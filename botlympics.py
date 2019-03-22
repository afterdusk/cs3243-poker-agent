import csv
import os
import random
from collections import deque
#from david_player import DavidPlayer
from wise_player import WisePlayer
from CLIENT_stadium import train_bots
from david_file_utils import *

# WELCOME TO THE BOT-LYMPICS!

LEADERBOARD = {}

def cacheBLboard(boardFileName):
    rawLeaderboard = getLeaderboard(boardFileName)
    leaderboard = {}
    for row in rawLeaderboard[1:]:
        name = row[2]
        print(name)
        botClass = row[1]
        stats = (0,0,0) # win, loss, perf
        weights = list(map(lambda e: float(e), row[7:]))
        remark = row[0]
        leaderboard[name] = [stats, weights, botClass, remark]
    return leaderboard

def writeToBLboardFile(leaderboard, boardFilename):
    HEADER = ('Remarks', 'Bot Class', 'Bot Name','Wins', 'Losses')
    fileContent = [HEADER]
    for agentName in leaderboard:
        stats = leaderboard[agentName][0]
        weights = leaderboard[agentName][1]
        botClass = leaderboard[agentName][2]
        remark = leaderboard[agentName][3]
        row = (remark, botClass, agentName, stats[0], stats[1], "Weights:") + tuple(weights)
        fileContent.append(row)

    with open(folderize(boardFilename), mode='w') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows(fileContent)
    writeFile.close()
def init(taskmaster):
    # CONFIGURATIONS
    LEADERBOARD_FILENAME = ["Botlympics"]

    global LEADERBOARD
    TASKMASTER = taskmaster

    def updateAgentsLeaderboardStats(winAgentName, loseAgentName):
        #updates the LEADERBOARD
        writeStats(winAgentName,LEADERBOARD, win=1)
        writeStats(loseAgentName,LEADERBOARD, lose=1)

    def wipeWinLoss():
        for name in LEADERBOARD:
            stats = getStats(name, LEADERBOARD)
            perf = stats[2]
            overwriteStats(name, LEADERBOARD, (0,0, perf))
    #================================
    #   Training related functions
    #================================
    def getRandomBotsFromBoard():
        botNameList = list(LEADERBOARD.keys())
        #print(leaderboard)
        first = random.choice(botNameList)
        second = random.choice(botNameList)
        while second == first:
            second = random.choice(botNameList)
        return (first,second)

    def beginTrainingAllBots(cycles):
        iterations = 0
        while iterations < cycles:
            bots = getRandomBotsFromBoard()
            arrangeMatch(bots[0], bots[1])
            iterations += 1

    def trainNamedBot(botName, botlist):
        # Trains with every other bot
        for opponent in botlist:
            if opponent == botName:
                continue
            arrangeLongMatch(botName,opponent)

    def roundRobinTraining():
        wipeWinLoss()
        print("ROUND ROBIN TRAINING")
        queuedMatches[0] = 0
        botlist = list(LEADERBOARD)
        line = 0
        for bot in botlist:
            print(bot)
            trainNamedBot(bot, botlist)

    #************================================************
    #         Server-Client communication functions
    #************================================************

    matchCountArr = [1]
    gens = [1]
    # Processes outcomes received from remote clients
    # Message contains a tuple of (winner_name,loser_name)
    def handleOutcome(sentJob, outcome):
        global LEADERBOARD
        boardLength = len(LEADERBOARD)
        UPDATE_BOARD_FREQUENCY = boardLength
        INCUBATE_FREQUENCY = queuedMatches[0] + 1

        print("\n============Training progress: " + str(matchCountArr[0]) + "/" + str(queuedMatches[0]) + "============")

        winnerName = sentJob[2][1-outcome]
        loserName = sentJob[2][outcome]
        updateAgentsLeaderboardStats(winnerName,loserName)

        if matchCountArr[0] >= UPDATE_BOARD_FREQUENCY and matchCountArr[0] % UPDATE_BOARD_FREQUENCY == 0:
            writeToBLboardFile(LEADERBOARD,LEADERBOARD_FILENAME[0])

        matchCountArr[0] = matchCountArr[0] + 1

    def jobDone(returnedJob,outcome):
        handleOutcome(returnedJob, outcome)

    # Sends a message to the clients in the form of a tuple
    # matchup_job = ((bot_1, bot_2), training_configuration, (b1Name, b2Name))
    def sendMatchup(matchup_job):
        print(str(matchup_job[2][0]) + " VERSUS " + str(matchup_job[2][1]))
        TASKMASTER.schedule_job(matchup_job, 120, jobDone)

    def composeBot(agentName):
        agentWeights = getWeights(agentName,LEADERBOARD)
        agentClassName = LEADERBOARD[agentName][2]
        return (agentClassName, agentWeights)

    # Composes the bots based on bot names
    queuedMatches = [0]

    # 100 games of 1000 rounds each
    def arrangeLongMatch(agentOneName, agentTwoName):
        botOne = composeBot(agentOneName)
        botTwo = composeBot(agentTwoName)
        num_games = 50
        num_rounds = 500
        training_regime = (num_games,num_rounds)
        # ((b1,b2), (ng,nr), (name1,name2))
        matchup_job = ((botOne, botTwo),training_regime,(agentOneName,agentTwoName))
        queuedMatches[0] = queuedMatches[0] + 1
        sendMatchup(matchup_job)

    # This is the main stuff
    try:
        LEADERBOARD = cacheBLboard(LEADERBOARD_FILENAME[0])
    except:
        print("ERROR " + LEADERBOARD_FILENAME[0] + ".csv not found!")
        exit()
    finally:
        roundRobinTraining()

    # MAIN
if __name__ == "__main__":
    print("THE BOTLYMPICS BEGINS!")
    class localCall():
        @staticmethod
        def schedule_job(match, timeout, callback):
            outcome = train_bots(match)
            callback(match, outcome)
            return
    init(localCall())
