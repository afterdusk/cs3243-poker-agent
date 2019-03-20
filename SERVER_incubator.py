import csv
import os
import random
import string
import math
from david_file_utils import *
# Handles the reinforcement learning. Creation of children and culling of weak agents

CHILD_THRESHOLD = 2
KILL_THRESHOLD = -2 #This will be flipped negative


def getMean(args):
    return sum(args) / len(args)

def getStdDev(args):
    mean = getMean(args)
    var  = sum(pow(a-mean,2) for a in args) / len(args)  # variance
    return math.sqrt(var)

def addAgent(agentName, weights, leaderboard):
    # Initialize win/loss/performace to 0,0,0
    #print("ADDING " + agentName)
    leaderboard[agentName] = [(0,0,0),weights]

#Removes the agent from the table
def removeAgent(agentName, leaderboard):
    #print("Removing " + agentName)
    #Table entry removal
    leaderboard.pop(agentName)

def updateAgentsLeaderboardPerf(goodOnes, badOnes, leaderboard):
    #print(goodOnes, badOnes)

    #updates the Agent_Leaderboard for PERFORMANCE
    totalPlayers = len(leaderboard)
    gl = min(len(goodOnes)//2, totalPlayers//4) #Extra reward
    for bot in goodOnes:
        stats = getStats(bot,leaderboard)
        performace = float(stats[2]) + 1
        if bot in goodOnes[:gl]:
            performace += 1

        if performace >= CHILD_THRESHOLD:
            makeChildFromParents(bot,random.choice(goodOnes), leaderboard)
            performace = 0

        writeStats(bot,leaderboard,perf=performace)

    bl = min(len(badOnes),totalPlayers//3) #Extra penalty
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
    def id_generator(size=4, chars=string.ascii_uppercase):
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

def applyToAll(bots, fun):
    for bot in bots:
        fun(bot)

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


def checkPlateau(old, new, numWeights):
    oldStats = evaluateBoard(old)
    newStats = evaluateBoard(new)
    print(oldStats,newStats)
    i = 0
    meanDiffs = 0
    stdDevDiffs = 0
    while i < numWeights:
        meanDiffs += abs(oldStats[i][0] - newStats[i][0])
        stdDevDiffs += abs(oldStats[i][1] - newStats[i][1])
        i += 1
    print("eval",meanDiffs,stdDevDiffs)
    return meanDiffs < 0.1 and (stdDevDiffs/numWeights < 0.02)


def incubate(leaderboard, numWeights, minBots):
    print("..........INCUBATING..........")
    gpThreshold = max(len(leaderboard)//3, 20)
    bpThreshold = max(len(leaderboard)//2, 20)

    oldBoard = leaderboard.copy()

    valueBoard = []
    for name in leaderboard:
        stats = getStats(name, leaderboard)
        currValue = evaluatePlayer(stats)
        valueBoard.append((currValue,name))

    valueBoard.sort(key=lambda tup: tup[0], reverse=True)
    goodPerformers = list(map(lambda t: t[1], valueBoard[:gpThreshold]))

    valueBoard.sort(key=lambda tup: tup[0])
    badPerformers = list(map(lambda t: t[1], valueBoard[:bpThreshold]))

    # Constant addition of 5 randoms
    leaderboard = spawnRandomChildren(3,leaderboard, numWeights)

    # Top up to meet minimum
    if len(leaderboard) < minBots:
        leaderboard = spawnRandomChildren(minBots - len(leaderboard),leaderboard, numWeights)


    updatedBoard = updateAgentsLeaderboardPerf(goodPerformers,badPerformers, leaderboard)

    plateauBool = checkPlateau(oldBoard, updatedBoard, numWeights)

    # Update the leaderboard
    print("..........FINISHED..........")
    return updatedBoard, plateauBool

def generateLeaderboard(boardFileName, numPlayers, numWeights):
    leaderboard = {}
    spawnRandomChildren(numPlayers, leaderboard, numWeights)
    writeToLeaderboardFile(leaderboard, 0, boardFileName)
    return leaderboard

if __name__ == "__main__":
    bn = "Agent_Board"
    #leaderboard = generateLeaderboard(bn, 50, 6)
    leaderboard = cacheLeaderboard(bn)
    newBoard, plateauBool = incubate(leaderboard, 6, 48)
    print(plateauBool)
    writeToLeaderboardFile(newBoard, 0, bn)
