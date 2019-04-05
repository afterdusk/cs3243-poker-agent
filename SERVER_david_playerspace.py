import csv
import os
import random
import time
from collections import deque
#from wise_player import WisePlayer
#from epsilon_player import EpsilonPlayer
from theta_player import ThetaPlayer
from lambda_player import LambdaPlayer
from CLIENT_stadium import train_bots
from SERVER_incubator import Incubator
from david_file_utils import *

# SERVER SIDE david_player trainer
# SERVER_script will call this

LEADERBOARD = {}
testing = 0

def init(taskmaster, boardName):
    # CONFIGURATIONS
    AGENT_CLASS = LambdaPlayer
    LEADERBOARD_FILENAME = [boardName] #Import boardname for continuity
    LEAGUE_MIN_SIZE = 256
    GENERATIONS_PER_CYCLE = 300 # Limit on number of generations per training
    SHRINK_RATE = 100 # League shrink per generation
    SHRINK_MAG = 1.5 # factor of shrink eqn
    NUM_GAMES = 3
    NUM_ROUNDS = 1000
    CHAMPION_BUFFER = 80
    PLATEAU_EVAL = [1]
    MY_INCUBATOR = Incubator(AGENT_CLASS)
    MY_INCUBATOR.enableStdPlayers()

    if testing:
        LEAGUE_MIN_SIZE = 30
        NUM_GAMES = 1
        NUM_ROUNDS = 10
        GENERATIONS_PER_CYCLE = 5
        #SHRINK_RATE = 16
        #CHAMPION_BUFFER = 3

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
        reduceLeagueSize()
        if gens[0] >= CHAMPION_BUFFER:
            MY_INCUBATOR.enableChamps()

        if MY_INCUBATOR.makeBackup():
            # Backup in case champions dominate
            writeToLeaderboardFile(LEADERBOARD, LEADERBOARD_FILENAME[0] + " (backup)", CURR_LEAGUE_SIZE[0], gens[0], PLATEAU_EVAL[0])

        LEADERBOARD, plateauBool, plateauVal = MY_INCUBATOR.incubate(LEADERBOARD, CURR_LEAGUE_SIZE[0])
        PLATEAU_EVAL[0] = plateauVal
        writeToLeaderboardFile(LEADERBOARD, LEADERBOARD_FILENAME[0], CURR_LEAGUE_SIZE[0], gens[0], plateauVal)

        with open(folderize(LEADERBOARD_FILENAME[0] + "_stats"),'a') as csvfile:
            row = ((str(gens[0]), str(PLATEAU_EVAL[0])),)
            writer = csv.writer(csvfile)
            writer.writerows(row)

        return plateauBool

    #************================================************
    #         Server-Client communication functions
    #************================================************

    matchCountArr = [1]
    gens = [0]
    # Processes outcomes received from remote clients
    # Message contains a tuple of (winner_name,loser_name)
    def handleOutcome(sentJob, stacks):
        global LEADERBOARD
        global MY_INCUBATOR
        boardLength = len(LEADERBOARD)
        UPDATE_BOARD_FREQUENCY = boardLength
        INCUBATE_FREQUENCY = queuedMatches[0] + 1
        outcome = stacks[0] >= stacks[1]

        print("\n============Training progress: " + str(matchCountArr[0]) + "/" + str(queuedMatches[0]) + "============")

        winnerName = sentJob[2][1-outcome]
        loserName = sentJob[2][outcome]
        updateAgentsLeaderboardStats(winnerName,loserName)

        if matchCountArr[0] >= UPDATE_BOARD_FREQUENCY and matchCountArr[0] % UPDATE_BOARD_FREQUENCY == 0:
            try:
                writeToLeaderboardFile(LEADERBOARD, LEADERBOARD_FILENAME[0], CURR_LEAGUE_SIZE[0],gens[0], PLATEAU_EVAL[0])
            except:
                print("Could not write to LEADERBOARD at this time",LEADERBOARD_FILENAME[0])

        matchCountArr[0] = matchCountArr[0] + 1

        if matchCountArr[0] >= INCUBATE_FREQUENCY:
            matchCountArr[0] = 1
            gens[0] = gens[0] + 1

            plateau = callIncubator()

            if gens[0] > GENERATIONS_PER_CYCLE or plateau:
                # Start a new training cycle

                gens[0] = 1
                # New incubator
                MY_INCUBATOR = Incubator(AGENT_CLASS)
                MY_INCUBATOR.enableStdPlayers()

                LEADERBOARD_FILENAME[0] = LEADERBOARD_FILENAME[0] + "I"
                exists = os.path.isfile(folderize(LEADERBOARD_FILENAME[0]))
                print("FOUND LEADERBOARD",LEADERBOARD_FILENAME[0])

                if exists:
                    try:
                        print("Reading from leaderboard!",LEADERBOARD_FILENAME[0])
                        LEADERBOARD, gens[0], CURR_LEAGUE_SIZE[0] = cacheLeaderboard(LEADERBOARD_FILENAME[0])
                        print("Read success!")
                    except:
                        print("Problem reading leaderboard!\nGENERATING NEW LEADERBOARD",LEADERBOARD_FILENAME[0])
                        LEADERBOARD = MY_INCUBATOR.generateLeaderboard(LEADERBOARD_FILENAME[0], LEAGUE_MIN_SIZE)
                        LEADERBOARD, gens[0], CURR_LEAGUE_SIZE[0] = cacheLeaderboard(LEADERBOARD_FILENAME[0])
                else:
                    print("GENERATING LEADERBOARD",LEADERBOARD_FILENAME[0])
                    LEADERBOARD = MY_INCUBATOR.generateLeaderboard(LEADERBOARD_FILENAME[0], LEAGUE_MIN_SIZE)
                    LEADERBOARD, gens[0], CURR_LEAGUE_SIZE[0] = cacheLeaderboard(LEADERBOARD_FILENAME[0])

                makeStatFile()

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

    # # This is the main stuff
    # LEADERBOARD, gens[0], CURR_LEAGUE_SIZE[0] = cacheLeaderboard(LEADERBOARD_FILENAME[0])
    def makeStatFile():
        with open(folderize(LEADERBOARD_FILENAME[0] + "_stats"),'a') as csvfile:
            row = (("Generation", "Winner STDDev"),)
            writer = csv.writer(csvfile)
            writer.writerows(row)

    makeStatFile()

    try:
        LEADERBOARD, gens[0], CURR_LEAGUE_SIZE[0] = cacheLeaderboard(LEADERBOARD_FILENAME[0])
        print("FOUND LEADERBOARD",LEADERBOARD_FILENAME[0])
    except:
        print("GENERATING LEADERBOARD",LEADERBOARD_FILENAME[0])
        LEADERBOARD = MY_INCUBATOR.generateLeaderboard(LEADERBOARD_FILENAME[0], LEAGUE_MIN_SIZE)
        LEADERBOARD, gens[0], CURR_LEAGUE_SIZE[0] = cacheLeaderboard(LEADERBOARD_FILENAME[0])
    finally:
        roundRobinTraining()

    # MAIN
if __name__ == "__main__":
    print("YOOOO")
    init("some","BOARDNAME")
