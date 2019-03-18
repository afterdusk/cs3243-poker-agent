import csv
import os
import random
import string
from david_file_utils import *
# Handles the reinforcement learning. Creation of children and culling of weak agents

CHILD_THRESHOLD = 2
KILL_THRESHOLD = -2 #This will be flipped negative

def addAgent(agentName, weights, leaderboard):
    print("ADDING " + agentName)
    # Initialize win/loss/performace to 0,0,0
    leaderboard[agentName] = [(0,0,0),weights]

#Removes the agent from the table
def removeAgent(agentName, leaderboard):
    print("Removing " + agentName)
    #Table entry removal
    leaderboard.pop(agentName)

def updateAgentsLeaderboardPerf(goodOnes, badOnes, leaderboard):
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
            perf = 0

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

    print("Created child " + child)

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

#def incubate(leaderboard):
def incubate(leaderboard, numWeights, minBots):
    print("..........INCUBATING..........")
    gpThreshold = max(len(leaderboard)//3, 20)
    bpThreshold = gpThreshold

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
    leaderboard = spawnRandomChildren(5,leaderboard, numWeights)

    # Top up to meet minimum
    if len(leaderboard) < minBots:
        leaderboard = spawnRandomChildren(minBots - len(leaderboard),leaderboard, numWeights)

    # Update the leaderboard
    print("..........FINISHED..........")
    return updateAgentsLeaderboardPerf(goodPerformers,badPerformers, leaderboard)

def generateLeaderboard(boardFileName, numPlayers, numWeights):
    leaderboard = {}
    spawnRandomChildren(numPlayers, leaderboard, numWeights)
    writeToLeaderboardFile(leaderboard, 0, boardFileName)
    return leaderboard

if __name__ == "__main__":
    leaderboard = cacheLeaderboard()
    newBoard = incubate(leaderboard, 6)
    writeToLeaderboardFile(newBoard, 0)
