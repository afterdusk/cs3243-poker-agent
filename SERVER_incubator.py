import csv
import os
import random
import string
import math
from david_file_utils import *
from argparse import ArgumentParser

# Handles the reinforcement learning. Creation of children and culling of weak agents

# Cloning of top 10%.
# Reproduction of top 10%
# Reward all winners
# Kill all losers ~50%

CHILD_THRESHOLD = 2
KILL_THRESHOLD = -1

def getMean(args):
    return sum(args) / len(args)

def getStdDev(args):
    mean = getMean(args)
    var  = sum(pow(a-mean,2) for a in args) / len(args)  # variance
    return math.sqrt(var)

def addAgent(agentName, weights, leaderboard):
    # Table entry addition
    # print("ADDING " + agentName)
    # Initialize win/loss/performace to 0,0,0
    leaderboard[agentName] = [(0,0,0),weights]

#Removes the agent from the table
def removeAgent(agentName, leaderboard):
    #Table entry removal
    #print("Removing " + agentName)
    leaderboard.pop(agentName)

# Mutates all data weights in steps of [-max to max] in either positive or negative direction
# If max > 1 then it resets to a default of 0.2
def mutateWeights(data, maxMutation):
    def bound(w):
        # Bounds between 1 and -1
        if w > 1:
            return 1
        if w < -1:
            return -1
        return w

    newData = []
    if maxMutation > 1 or maxMutation < -1:
        maxMutation = 0.2
    mutationBoundary = maxMutation*100
    for weight in data:
        newWeight = weight + (float(random.randint(-mutationBoundary,mutationBoundary))/100)
        newWeight = bound(newWeight)
        newData.append(newWeight)
    #print(data,newData)
    return newData

def makeClone(pName, board):
    parentW = getWeights(pName,board)
    childW = mutateWeights(parentW,0.05)
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

    #Muatate the weights by +/- 0.05
    mutateWeights(childWeights,0.05)
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
    rating = ratio * (wins+losses) + (wins-losses)
    return (wins > losses, ratio)

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
    PLATEAU_THRESHOLD = 0.009

    boardStats = evaluateBoard(board)
    print(boardStats)
    stdDevSum = 0
    i = 0
    while i < numWeights:
        stdDevSum += abs(boardStats[i][1])
        i += 1
    avgStdDev = stdDevSum/numWeights

    print("Evaluating: ", avgStdDev)
    return avgStdDev < PLATEAU_THRESHOLD, avgStdDev

def updateAgentsLeaderboardPerf(goodOnes, badOnes, leaderboard, minBots):
    #print(goodOnes, badOnes)
    #updates the Agent_Leaderboard for PERFORMANCE
    totalPlayers = len(leaderboard)

    # CLone top 10%
    top = goodOnes[:int(minBots//10)]
    for bot in top:
        makeClone(bot, leaderboard)

    # Stop having children growth

    # Limit
    rewardLimit = int(max(minBots/3, len(goodOnes)))

    #Extra Reward for 50% of good ones
    extraReward = int(len(goodOnes)//2)

    for bot in goodOnes[:rewardLimit]:
        if len(leaderboard) > int(1.3*minBots):
            break
        stats = getStats(bot,leaderboard)
        performace = float(stats[2]) + 1
        # Extra reward
        if bot in goodOnes[:extraReward]:
            performace += 1

        if performace >= CHILD_THRESHOLD:
            partner = random.choice(goodOnes)
            while partner == bot:
                partner = random.choice(goodOnes)
            makeChildFromParents(bot, partner, leaderboard)
            performace = 0

        writeStats(bot,leaderboard,perf=performace)


    # Gotta kill some goodOnes
    if totalPlayers > 1.5*minBots:
        cull = int(len(goodOnes)//5)
        badOnes.extend(goodOnes[cull:])

    toRemove = []
    for bot in badOnes:
        stats = getStats(bot,leaderboard)
        performace = float(stats[2]) - 5 #Kill instantly
        if performace <= KILL_THRESHOLD:
            toRemove.append(bot)
        else: #In case I want to preserve bad bots
            writeStats(bot,leaderboard,perf=performace)

    for bot in toRemove:
        removeAgent(bot, leaderboard)

    return leaderboard

# INCUBATE
def incubate(leaderboard, numWeights, minBots, champs):
    print("..........INCUBATING..........")
    # gpThreshold = int(len(leaderboard)//4) # Top 25%
    # bpThreshold = int(len(leaderboard)//1.667) # Bottom 60%
    valueBoard = []
    for name in leaderboard:
        stats = getStats(name, leaderboard)
        winlose, currValue = evaluatePlayer(stats)
        valueBoard.append((winlose, currValue, name))

    # BAD = Win:loss = 1:1 or worse
    badPerformers = list(filter(lambda tup: tup[0] == False, valueBoard))
    badPerformers.sort(key=lambda t:t[1])
    badPerformers = map(lambda t: t[2], badPerformers)

    goodPerformers = list(filter(lambda t: t[0] == True, valueBoard))
    goodPerformers.sort(key=lambda t:t[1], reverse=True)
    goodPerformers = map(lambda t: t[2], goodPerformers)

    updatedBoard = updateAgentsLeaderboardPerf(goodPerformers,badPerformers, leaderboard, minBots)
    plateauBool, plateauVal = checkPlateau(updatedBoard, numWeights)

    if plateauBool:
        print("Plateau detected!!")
    else:

        addStandardPlayers(updatedBoard,champs)

        # Top up to meet minimum
        if len(updatedBoard) < minBots:
            print("TOP UP "+ str(minBots - len(updatedBoard)))
            updatedBoard = spawnRandomChildren(minBots - len(updatedBoard), updatedBoard, numWeights)

        # if not len(updatedBoard) > 1.1*minBots:
        #     # Constant addition of 5% board size of randoms
        #     print("CURRENT BOARD LENGTH " + str(len(updatedBoard)))
        #     updatedBoard = spawnRandomChildren(minBots//20, updatedBoard, numWeights)
        #     print("Random bots spawned " + str(minBots//20))

    # Update the leaderboard
    print("..........FINISHED INCUBATION..........")
    return updatedBoard, plateauBool, plateauVal

# Add some consistent players
def addStandardPlayers(board, champs):
    STRONGPLAYERS = champs
    STANDARDPLAYERS = {}
    # these weights only work for EpsilonPlayer

    if STRONGPLAYERS:
        STANDARDPLAYERS['Ep_ZWUP'] = (0,0.05337793,0.214027344,0.035454102,0.025410156,-0.04884668,0.072243164,0.215789063,0.547893555,-0.60075293,0.425702148,-0.061788086)
        STANDARDPLAYERS['Ep_RNG'] = (0,-0.362,-0.699,0.535,0.022,-0.744,-0.767,0.79,0.895,-0.713,0.86,0.007)
        STANDARDPLAYERS['Ep_YRZX'] = (0,0.229223682,0.324028161,0.207622531,-0.532829859,-0.069627984,0.125704346,-0.083964584,0.595468388,-0.458556594,0.690242738,-0.018122754)
        STANDARDPLAYERS['E_Raiser'] = (0.438242914,0.004563298,-0.075314788,0.056284926,-0.06059732,-0.174429317,-0.086815867,0.015310329,0.160619342,-0.863199979,-0.350535249,0.181354672)
        STANDARDPLAYERS['Gr33DY'] = (0.62731144,0.006782764,0.0354006,-0.017738708,-0.060943432,-0.202364151,-0.059767574,0.033646709,0.744256733,0.183438671,-0.43500795,0.721879707)
    else:
        STANDARDPLAYERS['Raise'] = (0.7,0,0,0,0,0,0,0,-0.7,-0.8,0.1,0.3)
        STANDARDPLAYERS['Caller'] = (0.5,0,0,0,0,0,0,0,0.7,-0.7,-0.3,0.3)
        STANDARDPLAYERS['Greedy'] = (0.8,0,0,0,0,0,0,0,0.6,0.1,0.1,0.5)

    for name in STANDARDPLAYERS:
        if not name in board:
            w = STANDARDPLAYERS[name]
            addAgent(name,w, board)

def generateLeaderboard(boardFileName, numPlayers, numWeights):
    leaderboard = {}
    spawnRandomChildren(numPlayers, leaderboard, numWeights)
    addStandardPlayers(leaderboard, False)
    writeToLeaderboardFile(leaderboard, boardFileName)
    return leaderboard

if __name__ == "__main__":
    def parse():
        parser = ArgumentParser()
        parser.add_argument('-n', '--boardname', help="Name of board", default="evalboard", type=str)
        args = parser.parse_args()
        return args.boardname
    bn = parse()
    #bn = "OOC_G23"
    #leaderboard = generateLeaderboard(bn, 55, 12)
    leaderboard = cacheLeaderboard(bn)
    newBoard, plateauBool, platVal = incubate(leaderboard, 12, 55, True)
    #print("NEWBOARD LEN", len(newBoard))
    print(plateauBool)
    writeToLeaderboardFile(newBoard, bn)
