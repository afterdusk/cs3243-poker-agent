import csv
import os
import random
import string
import math
from david_file_utils import *
from argparse import ArgumentParser

# Handles the reinforcement learning. Creation of children and culling of weak agents

# Supports cloning of top 5%.
# Reproduction of top 10%
# Reward top 20%
# Penalize bottom 60%
# Kill bottom 40%

CHILD_THRESHOLD = 2
KILL_THRESHOLD = -2

def getMean(args):
    return sum(args) / len(args)

def getStdDev(args):
    mean = getMean(args)
    var  = sum(pow(a-mean,2) for a in args) / len(args)  # variance
    return math.sqrt(var)

def addAgent(agentName, weights, leaderboard):
    # Table entry addition
    #print("ADDING " + agentName)
    # Initialize win/loss/performace to 0,0,0
    leaderboard[agentName] = [(0,0,0),weights]

#Removes the agent from the table
def removeAgent(agentName, leaderboard):
    #Table entry removal
    #print("Removing " + agentName)
    leaderboard.pop(agentName)

def updateAgentsLeaderboardPerf(goodOnes, badOnes, leaderboard):
    #print(goodOnes, badOnes)
    #updates the Agent_Leaderboard for PERFORMANCE
    totalPlayers = len(leaderboard)

    # CLone top 5%
    top = goodOnes[:totalPlayers//20]
    for bot in top:
        makeClone(bot, leaderboard)

    gl = int(totalPlayers//10) #Extra reward for top 10%
    for bot in goodOnes:
        stats = getStats(bot,leaderboard)
        performace = float(stats[2]) + 1
        if bot in goodOnes[:gl]:
            performace += 1

        if performace >= CHILD_THRESHOLD:
            partner = random.choice(goodOnes)
            while partner == bot:
                partner = random.choice(goodOnes)
            makeChildFromParents(bot, partner, leaderboard)
            performace = 0

        writeStats(bot,leaderboard,perf=performace)

    #Extra penalty. Instant die
    bl = int(len(leaderboard)//2.5) #40%

    toRemove = []
    for bot in badOnes:
        stats = getStats(bot,leaderboard)
        performace = float(stats[2]) - 1
        if bot in badOnes[:bl]:
            performace -= 1
        if performace <= KILL_THRESHOLD:
            toRemove.append(bot)
        else:
            writeStats(bot,leaderboard,perf=performace)

    for bot in toRemove:
        removeAgent(bot, leaderboard)

    return leaderboard

# Mutates all data weights in steps of [-max to max] in either positive or negative direction
# If max > 1 then it resets to a default of 0.2
def mutateWeights(data, maxMutation):
    newData = []
    if maxMutation > 1 or maxMutation < -1:
        maxMutation = 0.2
    mutationBoundary = maxMutation*1000
    for weight in data:
        newWeight = weight + (float(random.randint(-mutationBoundary,mutationBoundary))/1000)
        newData.append(newWeight)
    #print(data,newData)
    return newData


def makeClone(pName, board):
    parentW = getWeights(pName,board)
    childW = mutateWeights(parentW,0.1)
    childName = pName + "^" + str(random.randint(0,9))
    addAgent(childName, childW, board)

def makeChildFromParents(botAName, botBName, leaderboard):
    parentAWeights = getWeights(botAName,leaderboard)
    parentBWeights = getWeights(botBName,leaderboard)
    #print(parentA,parentB)
    parentAPartName = botAName[:9]
    parentBPartName = botBName[:9]
    child = parentAPartName + "-" + parentBPartName + "#" + str(random.randint(0,99))

    # Add child to board
    childWeights = makeChildWeightsFromParents(parentAWeights,parentBWeights)
    addAgent(child, childWeights, leaderboard)
    #print("Created child " + child)

# Makes a child weight that takes the average of two parents and applies [+/-0.1] mutation
def makeChildWeightsFromParents(pAWeights, pBWeights):
    childWeights = []
    i = 0
    while i < len(pAWeights):
        # Takes the average of both parents
        childWeights.append((pAWeights[i]+pBWeights[i])/2)
        i+=1

    #Muatate the weights by +/- 0.1
    mutateWeights(childWeights,0.1)
    return childWeights

def generateRandomWeights(n):
    w = []
    while len(w) < n:
        w.append(0)
    return mutateWeights(w,0.9)

def spawnRandomChildren(num, leaderboard, numWeights):
    NAME_LENGTH = 4
    def id_generator(size=NAME_LENGTH, chars=string.ascii_uppercase):
        return ''.join(random.choice(chars) for _ in range(size))
    i = 0
    while i < num:
        botName = id_generator()
        weights = generateRandomWeights(numWeights)
        addAgent(botName, weights, leaderboard)
        i += 1

    return leaderboard
# Evaluation function based on wins/loss ratio and multiplied by number of games played
def evaluatePlayer(row):
    wins = float(row[0]) + 1
    losses = float(row[1]) + 1
    ratio = (wins/losses)
    final = ratio * (wins+losses) + (wins-losses)
    return final

# Gets the Mean and StdDev of the weights on a board
def evaluateBoard(board):
    weights = []
    for name in board:
        weights.append(getWeights(name,board))
    i = 0
    eval = []
    while i < len(weights[0]):
        currWeight = list(map(lambda x: x[i], weights))
        eval.append((getMean(currWeight), getStdDev(currWeight)))
        i += 1
    return eval

def checkPlateau(board, numWeights):
    # average Standard deviation
    PLATEAU_THRESHOLD = 0.05

    boardStats = evaluateBoard(board)
    stdDevSum = 0
    i = 0
    while i < numWeights:
        stdDevSum += abs(boardStats[i][1])
        i += 1
    avgStdDev = stdDevSum/numWeights

    print("Evaluating: ", avgStdDev)
    return avgStdDev < PLATEAU_THRESHOLD

def incubate(leaderboard, numWeights, minBots):
    print("..........INCUBATING..........")
    gpThreshold = int(len(leaderboard)//4) # Top 25%
    bpThreshold = int(len(leaderboard)//1.667) # Bottom 60%

    valueBoard = []
    for name in leaderboard:
        stats = getStats(name, leaderboard)
        currValue = evaluatePlayer(stats)
        valueBoard.append((currValue,name))

    valueBoard.sort(key=lambda tup: tup[0], reverse=True)
    goodPerformers = list(map(lambda t: t[1], valueBoard[:gpThreshold]))
    valueBoard.sort(key=lambda tup: tup[0])
    badPerformers = list(map(lambda t: t[1], valueBoard[:bpThreshold]))

    updatedBoard = updateAgentsLeaderboardPerf(goodPerformers,badPerformers, leaderboard)
    plateauBool = checkPlateau(updatedBoard, numWeights)

    if plateauBool:
        print("Plateau detected!!")
    else:
        # Constant addition of 8% board size of randoms
        updatedBoard = spawnRandomChildren(minBots//12.5,updatedBoard, numWeights)

        # Top up to meet minimum
        if len(leaderboard) < minBots:
            updatedBoard = spawnRandomChildren(minBots - len(leaderboard),updatedBoard, numWeights)

    # Update the leaderboard
    print("..........FINISHED INCUBATION..........")
    return updatedBoard, plateauBool

def generateLeaderboard(boardFileName, numPlayers, numWeights):
    leaderboard = {}
    spawnRandomChildren(numPlayers, leaderboard, numWeights)
    writeToLeaderboardFile(leaderboard, 0, boardFileName)
    return leaderboard

if __name__ == "__main__":
    def parse():
        parser = ArgumentParser()
        parser.add_argument('-n', '--boardname', help="Name of board", default="evalboard", type=str)
        args = parser.parse_args()
        return args.boardname
    bn = parse()
    #leaderboard = generateLeaderboard(bn, 90, 11)
    leaderboard = cacheLeaderboard(bn)
    newBoard, plateauBool = incubate(leaderboard, 11, 48)
    print(plateauBool)
    #writeToLeaderboardFile(newBoard, 0, bn)
