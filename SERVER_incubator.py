import csv
import os
import random
from CLIENT_test_arena import train_bots
from file_utils import folderize, readFileAndGetData, writeToFile

# Handles the reinforcement learning. Creation of children and culling of weak agents

def addAgentToBoard(agentName, weights):
    # Initialize win/loss/performace to 0,0,0
    newAgentRow = [agentName, 0, 0, 0]

    with open(folderize(MASTERFILE), mode='a') as boardFile:
        writer = csv.writer(boardFile)
        writer.writerow(newAgentRow)

#Removes the agent from the table and DELETES the csv file
def removeAgent(agentName):
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

    #Deletes the file
    os.remove(folderize(agentName))

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


def makeChildFromParents(parentA, parentB):
    parentAPartName = parentA[1][:8]
    parentBPartName = parentB[1][:8]
    child = parentAPartName + "-" + parentBPartName + "#" + str(random.randint(0,99))
    childWeights = makeChildWeightsFromParents(parentA[2], parentB[2])

    # Add child to board
    addAgentToBoard(child, childData[0])

    childData = (childWeights, [0,0,0])
    # Create new CSV for child
    writeToFile(child, childData)
    print("Created child " + child)

# Makes a child weight that takes the average of two parents and applies [+/-0.1] mutation

def makeChildWeightsFromParents(pAWeights, pBWeights):
    childWeights = []
    i = 0
    while i < len(aOWeights):
        # Takes the average of both parents
        childWeights.append((pAWeights[i]+pBWeights[i])/2)

    mutateWeights(childWeights,0.1)
    return childWeights

# Evaluation function based on wins/loss ratio and multiplied by number of games played
def evaluatePlayer(row):
    wins = int(row[1]) + 1
    losses = int(row[2]) + 1
    ratio = (wins/losses)
    final = ratio * (wins+losses) + (wins-losses)
    return final

# Increase performance
def reward():

# Decrease performance
def penalize():


def incubate(leaderboard):
    print("..........INCUBATING..........")
    gpThreshold = 5
    goodPerformers = [(0,"NULL"),]
    bpThreshold = 7
    badPerformers = []

    valueBoard = []
    for row in leaderboard[1:]:
        currName = row[0]
        currValue = evaluatePlayer(row)
        valueBoard.append((currValue,currName))

    valueBoard.sort(key=lambda tup: tup[0], reverse=True)
    goodPerformers = valueBoard[:gpThreshold]
    reward(goodPerformers)

    valueBoard.sort(key=lambda tup: tup[0])
    badPerformers = valueBoard[:bpThreshold]




    print(topFive)


    # Update the csv
    writeToFile(loserName,[data[0],newStats])
