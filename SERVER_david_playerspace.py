import csv
import os
import random
import time
from collections import deque
#from wise_player import WisePlayer
from epsilon_player import EpsilonPlayer
from CLIENT_stadium import train_bots
from SERVER_incubator import incubate, generateLeaderboard
from david_file_utils import *

# SERVER SIDE david_player trainer
# SERVER_script will call this

LEADERBOARD = {}
testing = 0
def init(taskmaster):
    # CONFIGURATIONS
    AGENT_CLASS = EpsilonPlayer
    LEADERBOARD_FILENAME = [str(time.time())[4:8]+"Ep_Board"]
    LEAGUE_MIN_SIZE = 256
    GENERATIONS_PER_CYCLE = 317 # Limit on number of generations per training
    SHRINK_RATE = 75 # League shrink per generation
    SHRINK_MAG = 2 # factor of shrink eqn
    NUM_GAMES = 3
    NUM_ROUNDS = 201
    CHAMPION_BUFFER = 100
    PLATEAU_EVAL = [1]

    if testing:
        LEAGUE_MIN_SIZE = 32
        NUM_GAMES = 1
        NUM_ROUNDS = 1
        SHRINK_RATE = 16
        SHRINK_MAG = 2
        CHAMPION_BUFFER = 3

    global LEADERBOARD
    CURR_LEAGUE_SIZE = [LEAGUE_MIN_SIZE]
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
            arrangeMatch(botName,opponent)

    def roundRobinTraining():
        wipeWinLoss()
        print("ROUND ROBIN TRAINING")
        queuedMatches[0] = 0
        botlist = list(LEADERBOARD)
        line = 0
        for bot in botlist:
            trainNamedBot(bot, botlist)

    def reduceLeagueSize():
        # reduce the league size
        reduction = int((CURR_LEAGUE_SIZE[0]/SHRINK_RATE)**SHRINK_MAG)
        CURR_LEAGUE_SIZE[0] = CURR_LEAGUE_SIZE[0] - reduction

    def callIncubator():
        global LEADERBOARD

        champBool = gens[0] > CHAMPION_BUFFER
        if gens[0] == CHAMPION_BUFFER:
            # Backup in case champions dominate
            writeToLeaderboardFile(LEADERBOARD, LEADERBOARD_FILENAME[0] + " (backup)",gens[0], PLATEAU_EVAL[0])
        LEADERBOARD, plateauBool, plateauVal = incubate(LEADERBOARD, AGENT_CLASS.number_of_weights, CURR_LEAGUE_SIZE[0], champBool)
        PLATEAU_EVAL[0] = plateauVal
        writeToLeaderboardFile(LEADERBOARD, LEADERBOARD_FILENAME[0],gens[0], PLATEAU_EVAL[0])
        return plateauBool

    #************================================************
    #         Server-Client communication functions
    #************================================************

    matchCountArr = [1]
    gens = [0]
    # Processes outcomes received from remote clients
    # Message contains a tuple of (winner_name,loser_name)
    def handleOutcome(sentJob, outcome):
        global LEADERBOARD
        boardLength = len(LEADERBOARD)
        UPDATE_BOARD_FREQUENCY = boardLength
        INCUBATE_FREQUENCY = queuedMatches[0]

        print("\n============Training progress: " + str(matchCountArr[0]) + "/" + str(queuedMatches[0]) + "============")

        winnerName = sentJob[2][1-outcome]
        loserName = sentJob[2][outcome]
        updateAgentsLeaderboardStats(winnerName,loserName)

        if matchCountArr[0] >= UPDATE_BOARD_FREQUENCY and matchCountArr[0] % UPDATE_BOARD_FREQUENCY == 0:
            writeToLeaderboardFile(LEADERBOARD, LEADERBOARD_FILENAME[0],gens[0], PLATEAU_EVAL[0])

        matchCountArr[0] = matchCountArr[0] + 1

        if matchCountArr[0] >= INCUBATE_FREQUENCY:
            matchCountArr[0] = 1
            gens[0] = gens[0] + 1

            plateau = callIncubator()

            if gens[0] > GENERATIONS_PER_CYCLE or plateau:
                gens[0] = 1
                LEADERBOARD_FILENAME[0] = LEADERBOARD_FILENAME[0] + "I"
                LEADERBOARD = generateLeaderboard(LEADERBOARD_FILENAME[0], LEAGUE_MIN_SIZE, AGENT_CLASS.number_of_weights)

            print("%%%%%%%%%%%%%%%%%%%%%% Beginning Generation "+ str(gens[0])+ "%%%%%%%%%%%%%%%%%%%%%%")
            roundRobinTraining()

    def jobDone(returnedJob,outcome):
        handleOutcome(returnedJob, outcome)

    # Sends a message to the clients in the form of a tuple
    # matchup_job = ((bot_1, bot_2), training_configuration, (b1Name, b2Name))
    def sendMatchup(matchup_job):
        TASKMASTER.schedule_job(matchup_job, 120, jobDone)

    def composeBot(agentName):
        agentWeights = getWeights(agentName,LEADERBOARD)
        agentClassName = AGENT_CLASS.__name__
        return (agentClassName, agentWeights)

    # Composes the bots based on bot names
    queuedMatches = [0]

    def arrangeMatch(agentOneName, agentTwoName):
        botOne = composeBot(agentOneName)
        botTwo = composeBot(agentTwoName)

        training_regime = (NUM_GAMES,NUM_ROUNDS)
        # ((b1,b2), (ng,nr), (name1,name2))
        matchup_job = ((botOne, botTwo),training_regime,(agentOneName,agentTwoName))

        sendMatchup(matchup_job)
        queuedMatches[0] = queuedMatches[0] + 1

    # This is the main stuff
    try:
        LEADERBOARD = cacheLeaderboard(LEADERBOARD_FILENAME[0])
    except:
        LEADERBOARD = generateLeaderboard(LEADERBOARD_FILENAME[0], LEAGUE_MIN_SIZE, AGENT_CLASS.number_of_weights)
        LEADERBOARD = cacheLeaderboard(LEADERBOARD_FILENAME[0])
    finally:
        roundRobinTraining()

    # MAIN
if __name__ == "__main__":
    print("YOOOO")
    init("some")
