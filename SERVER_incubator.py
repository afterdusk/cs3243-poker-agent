import csv
import os
import random
import string
from david_file_utils import readFileAndGetData, writeToFile, folderize
# Handles the reinforcement learning. Creation of children and culling of weak agents

CHILD_THRESHOLD = 1
KILL_THRESHOLD = -1 #This will be flipped negative

def addAgentToBoard(agentName,leaderboard):
    print("ADDING " + agentName)

    # Initialize win/loss/performace to 0,0,0
    leaderboard[agentName] = (0,0,0)

#Removes the agent from the table and DELETES the csv file
def removeAgent(agentName, leaderboard):
    #Deletes the csv file
    print("Removing " + agentName)
    os.remove(folderize(agentName))

    #Table entry removal
    leaderboard.pop(agentName)

def updateAgentsLeaderboardPerf(goodOnes, badOnes, leaderboard):
    #updates the Agent_Leaderboard for PERFORMANCE
    gl = min(len(goodOnes), 10) #Extra reward
    for bot in goodOnes:
        stats = leaderboard[bot]
        perf = float(stats[2]) + 1
        if bot in goodOnes[:gl]:
            perf += 1

        if perf >= CHILD_THRESHOLD:
            makeChildFromParents(bot,random.choice(goodOnes), leaderboard)
            perf = 0

        leaderboard[bot] = (stats[0], stats[1],perf)

    bl = min(len(badOnes),20) #Extra penalty
    toRemove = []
    for bot in badOnes:
        stats = leaderboard[bot]
        perf = float(stats[2]) - 1
        if bot in badOnes[:bl]:
            perf -= 1
        if perf <= KILL_THRESHOLD:
            toRemove.append(bot)
        else:
            leaderboard[bot] = (stats[0], stats[1],perf)

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
    parentA = readFileAndGetData(botAName)
    parentB = readFileAndGetData(botBName)
    #print(parentA,parentB)
    parentAPartName = botAName[:8]
    parentBPartName = botBName[:8]
    child = parentAPartName + "-" + parentBPartName + "#" + str(random.randint(0,99))

    # Add child to board
    addAgentToBoard(child, leaderboard)
    childWeights = makeChildWeightsFromParents(parentA[0], parentB[0])
    childData = (childWeights, [0,0,0])

    # Create new CSV for child
    writeToFile(child, childData)
    print("Created child " + child)

# Makes a child weight that takes the average of two parents and applies [+/-0.1] mutation
def makeChildWeightsFromParents(pAWeights, pBWeights):
    childWeights = []
    i = 0
    while i < 6:
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
    return mutateWeights(w,0.99)

def spawnRandomChildren(num, leaderboard):
    def id_generator(size=6, chars=string.ascii_uppercase):
        return ''.join(random.choice(chars) for _ in range(size))
    i = 0
    while i < num:
        botName = id_generator()
        weights = generateRandomWeights(6)
        addAgentToBoard(botName,leaderboard)
        writeToFile(botName, (weights,))
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

def incubate(leaderboard):
    FIXED_MIN_BOTS = 64
    print("..........INCUBATING..........")
    gpThreshold = max(len(leaderboard)//3, 30)
    bpThreshold = gpThreshold

    valueBoard = []
    for name in leaderboard:
        stats = leaderboard[name]
        currValue = evaluatePlayer(stats)
        valueBoard.append((currValue,name))

    valueBoard.sort(key=lambda tup: tup[0], reverse=True)
    goodPerformers = list(map(lambda t: t[1], valueBoard[:gpThreshold]))

    valueBoard.sort(key=lambda tup: tup[0])
    badPerformers = list(map(lambda t: t[1], valueBoard[:bpThreshold]))

    if len(leaderboard) < FIXED_MIN_BOTS:
        leaderboard = spawnRandomChildren(FIXED_MIN_BOTS - len(leaderboard),leaderboard)

    # Update the leaderboard
    print("..........FINISHED..........")
    return updateAgentsLeaderboardPerf(goodPerformers,badPerformers, leaderboard)
