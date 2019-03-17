import csv
import random
import os
from pypokerengine.players import BasePokerPlayer
from weighted_player import WeightedPlayer
from time import sleep
import pprint

MASTERFILE = "Agent_Leaderboard"

CHILD_THRESHOLD = 80
KILL_THRESHOLD = 9

# References the folder and file extension
def folderize(filename):
    return os.getcwd()+"/player-seeds/" + filename + ".csv"


def writeToFile(filename, *data):
    contentToWrite = data[0]
    with open(folderize(filename), mode='w') as outputFile:
        myWriter = csv.writer(outputFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in contentToWrite:
            #print("Row: ", row)
            myWriter.writerow(row)

        outputFile.close()

def readFileAndGetData(filename):
    with open(folderize(filename)) as csvFile:
        csvReader = csv.reader(csvFile, delimiter= ',')
        line = 0
        data = []
        for row in csvReader:
            parsed_row = []
            if line == 0:
                print(row)
                for e in row:
                    if len(e) > 0:
                        parsed_row.append(float(e))
                    else:
                        parsed_row.append(e)
                data.append(parsed_row)
            else:
                data.append(row)
            line += 1
        #print('\nProcessed '+ str(line) +' lines\n')
        csvFile.close()
        return data
def removeAgent(agentName):
    #Removes the agent from the table
    table = []
    with open(folderize(MASTERFILE), mode='r') as readFile:
        csvReader = csv.reader(readFile,  delimiter= ',')
        for currRow in csvReader:
            if currRow[0] == agentName:
                continue
            table.append(currRow)
    readFile.close()

    #Deletes the file
    os.remove(folderize(agentName))

    with open(folderize(MASTERFILE), mode='w') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows(table)
    writeFile.close()

def addAgentToBoard(agentName, weights):
    # Initialize win/loss to 0,0
    newAgentRow = [agentName, 0, 0, 0]
    #for e in weights:
    #    newAgent.append(e)

    with open(folderize(MASTERFILE), mode='a') as boardFile:
        writer = csv.writer(boardFile)
        writer.writerow(newAgentRow)

def editAgentsOnBoard(winAgent, loseAgent):
    #updates the Agent_Leaderboard
    oldInfo = []
    with open(folderize(MASTERFILE)) as readFile:
        csvReader = csv.reader(readFile,  delimiter= ',')
        rows = list(csvReader)
    readFile.close()

    with open(folderize(MASTERFILE)) as readFile:
        csvReader = csv.reader(readFile,  delimiter= ',')
        line = 0
        winLine = 0
        loseLine = 0
        for row in csvReader:
            if row[0] == winAgent.filename:
                winLine = [line, row]
            if row[0] == loseAgent.filename:
                loseLine = [line,row]
            line += 1
        oldInfo = (winLine,loseLine)
    readFile.close()

    newWinRow = oldInfo[0][1]
    newWinRow[1] = int(newWinRow[1]) + 1
    newWinRow[3] = winAgent.perf
    newLoseRow = oldInfo[1][1]
    newLoseRow[2] = int(newLoseRow[2]) + 1
    newLoseRow[3] = loseAgent.perf
    rows[oldInfo[0][0]] = newWinRow
    rows[oldInfo[1][0]] = newLoseRow
    with open(folderize(MASTERFILE), mode='w') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows(rows)
    writeFile.close()

# Mutates all data weights in steps of [0.01 - 0.10] in either positive or negative direction
def mutateData(data):
    newData = []
    for e in data:
        newWeight = e
        mutation = random.randint(-1, 1)
        if mutation < 0:
            newWeight = e - (float(random.randint(10,600))/1000)
        elif mutation > 0:
            newWeight = e + (float(random.randint(10,600))/1000)
        newData.append(newWeight)
    print(data,newData)
    return newData

# A wrapper class for players
class MyTrainablePlayer():
    def __init__(self, filename):
        self.filename = filename
        raw = readFileAndGetData(filename)
        print("raw: ", raw)
        self.weights = raw[0]
        #generate missing weights
        i = 0
        while i < 7:
            if self.weights[i] == "":
                gen = float(random.randint(-99,99))/100
                self.weights[i] = gen
            i+=1
        winlossperf = raw[1]
        self.wins = int(winlossperf[0])
        self.losses = int(winlossperf[1])
        self.perf = int(winlossperf[2])
        # if self.losses - self.wins > 2:
        #     print(filename + " is a losing agent")
        self.player = WeightedPlayer()
        self.player.initWeights(self.weights)

    def updateSelf(self):
        #update number of wins/losses/performance
        writeToFile(self.filename, (self.weights,[self.wins,self.losses,self.perf]))
        print("Current w/l/p for " + self.filename + " = " + str(self.wins) + "/" + str(self.losses) + "/" + str(self.perf))

    def makeChild(self):
        child = self.filename + "-" + str(random.randint(0,99))
        childData = (mutateData(self.weights), [0,0,0])
        # Add child to board
        addAgentToBoard(child, childData[0])
        # Create new CSV for child
        writeToFile(child, childData)
        print("Created child " + child)

    def reward(self,opponent):
        self.wins += 1
        self.perf += 1
        if self.perf >= CHILD_THRESHOLD:
            self.perf = 1
            # Make 2 children!
            self.makeChild()
            self.makeChild()

        editAgentsOnBoard(self, opponent)
        self.updateSelf()

    def deward(self):
        self.losses += 1
        self.perf -=1
        if self.losses - self.wins > KILL_THRESHOLD:
            removeAgent(self.filename)
            print("\nAGENT HAS BEEN KILLED " + self.filename + "\n")
            return self.filename
        else:
            self.updateSelf()
            return ""

    def getPlayer(self):
        return self.player
