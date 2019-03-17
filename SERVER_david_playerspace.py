import csv
import os
import random
from collections import deque
from CLIENT_stadium import train_bots
from SERVER_incubator import incubate
from david_file_utils import folderize, readFileAndGetData, writeToFile, getLeaderboard, MASTERFILE

LEADERBOARD = {}

# SERVER_script will call this
def init(taskmaster):
    TASKMASTER = taskmaster

    # SERVER SIDE david_player trainer
    def cacheLeaderboard():
        global LEADERBOARD
        rawLeaderboard = getLeaderboard(MASTERFILE)

        for row in rawLeaderboard[1:]:
            name = row[0]
            scores = tuple(map(lambda e: float(e), row[1:]))
            LEADERBOARD[name] = scores
        #print(LEADERBOARD)

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
        global LEADERBOARD
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

    def trainNamedBot(botName, botlist):
        # Trains with every other bot
        for opponent in botlist:
            if opponent == botName:
                continue
            arrangeMatch(botName,opponent)

    def roundRobinTraining():
        #print("ROUND ROBIN TRAINING")
        botlist = list(LEADERBOARD)
        line = 0
        for bot in botlist:
            trainNamedBot(bot, botlist)

    #************================================************
    #         Server-Client communication functions
    #************================================************

    matchCount = 1
    # Processes outcomes received from remote clients
    # Message contains a tuple of (winner_name,loser_name)
    def handleOutcome(sentJob, outcome):
        global matchCount
        print("\n============Overall Match number: " + str(matchCount) +"============")

        # global INCUBATEFREQUENCY
        if outcome == 1:
            winnerName = sentJob[2][0]
            loserName = sentJob[2][1]
        else:
            winnerName = sentJob[2][1]
            loserName = sentJob[2][0]

        updateAgentsLeaderboardStats(winnerName,loserName)
        matchCount += 1

    # Sends a message to the clients in the form of a tuple
    # matchup_job = ((bot_1, bot_2), training_configuration, (b1Name, b2Name))
    def sendMatchup(matchup_job):
        #print(matchup_job)
        TASKMASTER.schedule_job(matchup_job, 120, handleOutcome)

    def composeBot(agentName):
        data = readFileAndGetData(agentName)
        agentWeights = data[0]
        agentStats = data[1]
        agentClassName = "DavidPlayer"
        return (agentClassName, agentWeights)

    # TODO: Move this to somewhere less awkward
    matchup_queue = deque()

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

    NUM_GENERATIONS = 5
    # This is the main training
    cacheLeaderboard()
    i = 0
    while i < NUM_GENERATIONS:
        roundRobinTraining()
        writeToLeaderboardFile()
        #incubate()
        print("\n\n%%%%%%%%%%%%%%%%%%%%%% Finished Generation " + str(i+1) +"%%%%%%%%%%%%%%%%%%%%%%\n\n")
        i += 1

    # MAIN
    if __name__ == "__main__":
        cacheLeaderboard()
        roundRobinTraining()
