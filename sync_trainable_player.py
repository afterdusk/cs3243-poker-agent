import csv
import random
import os
from pypokerengine.players import BasePokerPlayer
from weighted_player import WeightedPlayer
from time import sleep

CHILD_THRESHOLD = 80
KILL_THRESHOLD = 9

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
class MySyncablePlayer():
    def __init__(self, bot):
        self.filename = bot[1]
        self.weights = bot[2]
        winlossperf = bot[3]
        #generate missing weights
        i = 0
        while i < 7:
            if self.weights[i] == "":
                gen = float(random.randint(-99,99))/100
                self.weights[i] = gen
            i+=1
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
