import csv
import os
import random
from file_utils import folderize, readFileAndGetData, writeToFile, MASTERFILE

# Handles the reinforcement learning. Creation of children and culling of weak agents

CHILD_THRESHOLD = 12
KILL_THRESHOLD = 7 #This will be flipped negative


def addAgentToBoard(agentName):
    print("ADDING " + agentName)

    # Initialize win/loss/performace to 0,0,0
    newAgentRow = [agentName, 0, 0, 0]

    with open(folderize(MASTERFILE), mode='a') as boardFile:
        writer = csv.writer(boardFile)
        writer.writerow(newAgentRow)

#Removes the agent from the table and DELETES the csv file
def removeAgent(agentName):
    #Deletes the csv file
    print("Removing " + agentName)
    os.remove(folderize(agentName))

    #Table entry removal
    table = []
    with open(folderize(MASTERFILE), mode='r') as readFile:
        csvReader = csv.reader(readFile,  delimiter= ',')
        for currRow in csvReader:
            if currRow[0] == agentName:
                continue
            table.append(currRow)

    readFile.close()
    with open(folderize(MASTERFILE), mode='w') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows(table)
    writeFile.close()


def updateAgentsLeaderboardPerf(goodOnes, badOnes):
    #updates the Agent_Leaderboard for PERFORMANCE
    with open(folderize(MASTERFILE)) as readFile:
        csvReader = csv.reader(readFile,  delimiter= ',')
        rows = list(csvReader)
    readFile.close()

    changeRows = []
    toRemove = []
    line = 0
    for row in rows:
        if row[0] in goodOnes:
            newRow = row
            perf = float(row[3]) + 1
            # Top 3
            if row[0] in goodOnes[:2]:
                perf += 1.5
            if perf > CHILD_THRESHOLD:
                makeChildFromParents(row[0],goodOnes[1])
                perf = 0
            newRow[3] = perf
            changeRows.append((line, newRow))

        if row[0] in badOnes:
            newRow = row
            perf = float(row[3]) - 1
            # Worst 1
            if row[0] == badOnes[0]:
                perf -= 1

            if -1*perf > KILL_THRESHOLD:
                toRemove.append(row[0])
            else:
                newRow[3] = perf
                changeRows.append((line,newRow))
        line += 1

    for changed in changeRows:
        index = changed[0]
        content = changed[1]
        rows[index] = content

    for bot in toRemove:
        removeAgent(bot)

    with open(folderize(MASTERFILE), mode='w') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows(rows)
    writeFile.close()

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


def makeChildFromParents(botAName, botBName):
    parentA = readFileAndGetData(botAName)
    parentB = readFileAndGetData(botBName)
    print(parentA,parentB)
    parentAPartName = botAName[:8]
    parentBPartName = botBName[:8]
    child = parentAPartName + "-" + parentBPartName + "#" + str(random.randint(0,99))

    # Add child to board
    addAgentToBoard(child)

    childWeights = makeChildWeightsFromParents(parentA[0], parentB[0])

    childData = (childWeights, [0,0,0])
    # Create new CSV for child
    writeToFile(child, childData)
    print("Created child " + child)

# Makes a child weight that takes the average of two parents and applies [+/-0.1] mutation

def makeChildWeightsFromParents(pAWeights, pBWeights):
    childWeights = []
    i = 0
    while i < len(pAWeights):
        # Takes the average of both parents
        childWeights.append((pAWeights[i]+pBWeights[i])/2)
        i+=1

    mutateWeights(childWeights,0.1)
    return childWeights

# Evaluation function based on wins/loss ratio and multiplied by number of games played
def evaluatePlayer(row):
    wins = int(row[1]) + 1
    losses = int(row[2]) + 1
    ratio = (wins/losses)
    final = ratio * (wins+losses) + (wins-losses)
    return final

# Increase performance on LOCAL FILE
def reward(bot):
    stats = readFileAndGetData(bot)
    stats[1][2] = int(stats[1][2]) + 1
    writeToFile(bot,stats)

# Decrease performance on LOCAL FILE
def penalize(bot):
    stats = readFileAndGetData(bot)
    stats[1][2] = int(stats[1][2]) - 1
    writeToFile(bot,stats)


def applyToAll(bots, fun):
    for bot in bots:
        fun(bot)

def incubate(leaderboard):
    print("..........INCUBATING..........")
    gpThreshold = 7
    goodPerformers = []
    bpThreshold = 9
    badPerformers = []

    valueBoard = []
    for row in leaderboard[1:]:
        currName = row[0]
        currValue = evaluatePlayer(row)
        valueBoard.append((currValue,currName))

    valueBoard.sort(key=lambda tup: tup[0], reverse=True)
    goodPerformers = list(map(lambda t: t[1], valueBoard[:gpThreshold]))


    valueBoard.sort(key=lambda tup: tup[0])
    badPerformers = list(map(lambda t: t[1], valueBoard[:bpThreshold]))

    # updates Individual local agent files
    # Screw it
    # applyToAll(goodPerformers, reward)
    # applyToAll(badPerformers, penalize)

    # Update the leaderboard
    updateAgentsLeaderboardPerf(goodPerformers,badPerformers)
