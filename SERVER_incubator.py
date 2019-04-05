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


STANDARD_PLAYER_FLAG = False
CHILD_THRESHOLD = 2
KILL_THRESHOLD = -1

class Incubator():
    WEIGHT_BOUNDS = []

    # Takes in a player class
    def __init__(self, pc):
        self.numWeights = pc.number_of_weights
        self.champs = False
        self.backup = 0
        self.initWeightBounds()
        self.SPF = False

    def initWeightBounds(self):
        nw = self.numWeights
        self.WEIGHT_BOUNDS = []
        for i in range(0,nw):
            self.WEIGHT_BOUNDS.append([-1,1]) # Lower, Upper

    def enableChamps(self):
        self.champs = True
        if self.backup == 0:
            self.backup = 1

    def enableStdPlayers(self):
        self.SPF = True

    def makeBackup(self):
        if self.backup == 1:
            self.backup = 2
            return True
        return False

    # Tightens the bounds based on a bunch of very lousy bots
    def tightenWeightBounds(self,leaderboard, badBots):
        positiveBoardStats = evaluateBoard(leaderboard)
        for weightIndex in range(0,len(positiveBoardStats)):
            w_mean, w_stdev = positiveBoardStats[weightIndex]
            TIGHTEN_THRESHOLD = 3*w_stdev # !!! CONFIGURE BOUND CONDITIONS HERE !!!
            for name in badBots:
                badWeight = badBots[name][weightIndex]
                meanDiff = badWeight - w_mean
                if badWeight > self.WEIGHT_BOUNDS[weightIndex][0] and badWeight < self.WEIGHT_BOUNDS[weightIndex][1]:
                    if meanDiff < 0:
                        # If higher than lower bound
                        if abs(meanDiff) > TIGHTEN_THRESHOLD:
                            print("Tightening Lower bound",weightIndex,self.WEIGHT_BOUNDS[weightIndex][0], badWeight)
                            self.WEIGHT_BOUNDS[weightIndex][0] = badWeight

                    elif meanDiff > 0:
                        # If lower than upper bound
                        if abs(meanDiff) > TIGHTEN_THRESHOLD:
                            print("Tightening Upper bound",weightIndex,self.WEIGHT_BOUNDS[weightIndex][1], badWeight)
                            self.WEIGHT_BOUNDS[weightIndex][1] = badWeight

    # Mutates all data weights in steps of [-max to max] in either positive or negative direction
    # If max > 1 then it resets to a default of 0.2
    def mutateWeights(self, data, maxMutation):
        multi = 100000
        def getBounds(weight, mutation, i):
            # Bounds for each weight
            # Second part is so boundaries never get reversed
            high = max(min(weight+mutation, self.WEIGHT_BOUNDS[i][1]), self.WEIGHT_BOUNDS[i][0])
            low = min(max(weight-mutation, self.WEIGHT_BOUNDS[i][0]), self.WEIGHT_BOUNDS[i][1])
            if low > high:
                print("ERROR WEIGHT BOUNDARIES REVERSED")
            return int(multi*low), int(multi*high)

        i = 0
        newData = []
        for weight in data:
            lowerBound, upperBound = getBounds(weight,maxMutation, i)
            newWeight = float(random.randint(lowerBound,upperBound))/multi
            #print(lowerBound, upperBound, newWeight)
            newData.append(newWeight)
            i+=1
        #print(data,newData)
        return newData

    def generateRandomWeights(self,n):
        w = []
        while len(w) < n:
            w.append(0)
        return self.mutateWeights(w,0.9)

    def makeClone(self, pName, board):
        parentW = getWeights(pName,board)
        MOVEMENT = 0.02
        # Gradient descent?
        # Creates 2*W clones
        i = 0
        while i < len(parentW):
            childW = parentW
            childW[i] = childW[i] + MOVEMENT
            childName = pName + "^" + str(i)
            addAgent(childName, childW, board)

            childW = parentW
            childW[i] = childW[i] - MOVEMENT
            childName = pName + "^" + str(i+1)
            addAgent(childName, childW, board)
            i += 2

    def makeChildFromParents(self, botAName, botBName, leaderboard):
        # Makes a child weight that takes the average of two parents and applies [+/-0.1] mutation
        def makeChildWeightsFromParents(pAWeights, pBWeights):
            childWeights = []
            for i in range(0,len(pAWeights)):
                # Takes the average of both parents
                childWeights.append((pAWeights[i]+pBWeights[i])/2)

            #Muatate the weights by +/- 0.05
            self.mutateWeights(childWeights,0.05)
            return childWeights

        parentAWeights = getWeights(botAName,leaderboard)
        parentBWeights = getWeights(botBName,leaderboard)
        childWeights = makeChildWeightsFromParents(parentAWeights,parentBWeights)
        childName = botAName[:12] + "-" + botBName[:12] + "#" + str(random.randint(0,99))

        # Add child to board
        addAgent(childName, childWeights, leaderboard)
        #print("Created child " + child)

    def spawnRandomChildren(self, num, leaderboard, numWeights):
        NAME_LENGTH = 4
        def id_generator(size=NAME_LENGTH, chars=string.ascii_uppercase):
            return ''.join(random.choice(chars) for _ in range(size))
        i = 0
        while i < num:
            botName = id_generator()
            weights = self.generateRandomWeights(numWeights)
            addAgent(botName, weights, leaderboard)
            i += 1
        return leaderboard

    # INCUBATE!
    def incubate(self,leaderboard, minBots):
        numWeights = self.numWeights
        print("..........INCUBATING..........")
        self.initWeightBounds() #RESTART THIS EVERY TIME

        # gpThreshold = int(len(leaderboard)//4) # Top 25%
        # bpThreshold = int(len(leaderboard)//1.667) # Bottom 60%

        valueBoard = []
        for name in leaderboard:
            stats = getStats(name, leaderboard)
            winlose, currValue = evaluatePlayer(stats)
            valueBoard.append((winlose, currValue, name))

        # BAD = Winrate <= 50%
        badPerformers = list(filter(lambda tup: tup[0] == False, valueBoard))
        badPerformers.sort(key=lambda t:t[1])
        badPerformers = map(lambda t: t[2], badPerformers)

        goodPerformers = list(filter(lambda t: t[0] == True, valueBoard))
        goodPerformers.sort(key=lambda t:t[1], reverse=True)
        goodPerformers = map(lambda t: t[2], goodPerformers)

        updatedBoard = updateLeaderboardPerf(self, goodPerformers,badPerformers, leaderboard, minBots)
        plateauBool, plateauVal = checkPlateau(updatedBoard, numWeights)

        stopTraining = plateauBool and self.champs

        if plateauBool:
            print("Plateau detected!!")
            self.enableChamps()
        else:
            addStandardPlayers(updatedBoard,self)

            # Top up to meet minimum
            if len(updatedBoard) < minBots:
                print("TOP UP "+ str(minBots - len(updatedBoard)))
                updatedBoard = self.spawnRandomChildren(minBots - len(updatedBoard), updatedBoard, numWeights)


        print("..........FINISHED INCUBATION..........")
        return updatedBoard, stopTraining, plateauVal


    def generateLeaderboard(self, boardFileName, numPlayers):
        numWeights = self.numWeights
        leaderboard = {}
        self.spawnRandomChildren(numPlayers, leaderboard, numWeights)
        addStandardPlayers(leaderboard, self)
        writeToLeaderboardFile(leaderboard, boardFileName,numPlayers)
        return leaderboard


# DESTROY AND REPRODUCE
# Also updates the Leaderboard for PERFORMANCE
def updateLeaderboardPerf(incubator, goodOnes, badOnes, leaderboard, minBots):
    #print(goodOnes, badOnes)
    totalPlayers = len(leaderboard)

    # &&&&&&&&&&&&&&&&&&&&&&&&&& Cull weak players &&&&&&&&&&&&&&&&&&&&&&&&&&
    # If pop too high, gotta kill some goodOnes
    if totalPlayers > 1.5*minBots:
        cull = int(len(goodOnes)//5)
        goodOnes = goodOnes[:cull] # Shorten goodOnes
        badOnes.extend(goodOnes[cull:])

    toRemove = []
    superBad = {}
    superBad_T = int(max(len(badOnes)//4, 5))
    for bot in badOnes:
        stats = getStats(bot,leaderboard)
        performace = float(stats[2]) - 5 #Kill instantly
        if bot in badOnes[:superBad_T]:
            # Record for weight bound adjustment
            superBad[bot] = getWeights(bot,leaderboard)
        if performace <= KILL_THRESHOLD:
            toRemove.append(bot)
        else: #In case I want to preserve bad bots
            writeStats(bot,leaderboard,perf=performace)

    for bot in toRemove:
        removeAgent(bot, leaderboard)

    incubator.tightenWeightBounds(leaderboard, superBad)

    # Update value of totalPlayers
    totalPlayers = len(leaderboard)

    # &&&&&&&&&&&&&&&&&&&&&&&&&& Reward good players &&&&&&&&&&&&&&&&&&&&&&&&&&
    # CLone top 4%
    for bot in goodOnes[:int(minBots//25)]:
        incubator.makeClone(bot, leaderboard)

    # Limit
    rewardLimit = int(min(minBots/3, len(goodOnes)))
    #Extra Reward for 50% of good ones
    extraReward = int(len(goodOnes)//2)

    for bot in goodOnes[:rewardLimit]:
        if len(leaderboard) > int(1.5*minBots):
            # Prevent super overpopulation
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
            incubator.makeChildFromParents(bot, partner, leaderboard)
            performace = 0

        writeStats(bot,leaderboard,perf=performace)

    return leaderboard

def getMean(args):
    return sum(args) / len(args)

def getStdDev(args):
    mean = getMean(args)
    var  = sum(pow(a-mean,2) for a in args) / len(args)  # variance
    return math.sqrt(var)

# Table entry addition
def addAgent(agentName, weights, leaderboard):
    # print("ADDING " + agentName)
    leaderboard[agentName] = [(0,0,0),weights]    # Initialize win/loss/performace to 0,0,0

#Removes the agent from the table
def removeAgent(agentName, leaderboard):
    #print("Removing " + agentName)
    leaderboard.pop(agentName)

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
        #print("Weight " + str(i),getMean(currWeight), getStdDev(currWeight))
        eval.append((getMean(currWeight), getStdDev(currWeight)))
        i += 1
    return eval

def checkPlateau(board, numWeights):
    # average Standard deviation
    PLATEAU_THRESHOLD = 0.007

    boardStats = evaluateBoard(board)
    stdDevSum = 0
    i = 0
    while i < numWeights:
        stdDevSum += abs(boardStats[i][1])
        i += 1
    avgStdDev = stdDevSum/numWeights

    print("Plateau evaluation: ", avgStdDev, "Threshold:", PLATEAU_THRESHOLD)
    return avgStdDev < PLATEAU_THRESHOLD, avgStdDev

# Add some consistent players
# these weights only work for EpsilonPlayer
def addStandardPlayers(board, incubator):
    def parseTPWeights(*weights):
        # Parse ThetaPlayer weights
        lambda_w = []
        lambda_w.extend(weights[:5])
        lambda_w.append(weights[7]+weights[12])
        lambda_w.extend(weights[8:12])
        lambda_w.extend(4*[weights[5],])
        lambda_w.extend(4*[weights[6],])
        return lambda_w

    champs = incubator.champs
    if not incubator.SPF:
        return

    STANDARDPLAYERS = {}
    # SANITY CHECK
    STANDARDPLAYERS['Raiz'] = parseTPWeights(0.4,0.05,0.05,-0.05,-0.05,0,0,0,-0.8,-0.8,0,0.5,0,0)

    if champs:

        # Epsilon Ported
        STANDARDPLAYERS['Acnd'] = parseTPWeights(0.45854458*2,-0.010288565,0.023143473,0.003357603,-0.045208527,-0.291372468,0.012108953,-0.14727149,0.456158875,-0.156368715,-0.575275254*2,0.717262457,0,0)
        STANDARDPLAYERS['Cal9'] = parseTPWeights(0.027780254*2,-0.006881324,-0.02755483,0.052425943,-0.247408722,-0.343405448,-0.092064001,-0.114631729,0.367807581,-0.466988527,-0.449206837*2,0.577756734,0,0)
        STANDARDPLAYERS['Lion'] = parseTPWeights(0.472384782*2,-0.013161448,0.025753558,0.006890752,-0.040231418,-0.293013775,0.014284528,-0.153108951,0.464752312,-0.170325176,-0.574609741*2,0.734561248,0,0)
        STANDARDPLAYERS['G3Dy'] = parseTPWeights(0.62731144*2,0.006782764,0.0354006,-0.017738708,-0.060943432,-0.202364151,-0.059767574,0.033646709,0.744256733,0.183438671,-0.43500795*2,0.721879707,0,0)
        # Theta
        STANDARDPLAYERS['Omeg'] = parseTPWeights(0.4634,-0.021305,-0.02627,0.029645,-0.013075,-0.34785,-0.06516,-0.09723,0.410035,-0.095695,-0.550825,0.71539,0.039705,-0.02993)
        STANDARDPLAYERS['WrtH'] = parseTPWeights(0.457495,-0.03758,-0.010125,-0.04319,-0.050635,-0.327235,-0.05119,-0.11063,0.420975,-0.08234,-0.54522,0.737925,-0.016405,0.04441)
        STANDARDPLAYERS['OmX2'] = parseTPWeights(0.457895,0.0253075,0.01069,0.0101225,0.0025675,-0.34887,-0.01472,-0.10998,0.3922275,-0.1183975,-0.5474175,0.7205655,0.0253325,-0.05307)
        STANDARDPLAYERS['Pr1D'] = parseTPWeights(0.48393,-0.0370925,-0.03515,0.0109875,-0.0227425,-0.350185,-0.0771,-0.07662,0.4209825,-0.1094175,-0.5335175,0.719145,0.0159975,-0.01311)
        STANDARDPLAYERS['MG3d'] = parseTPWeights(0.85901144,-0.007261118,0.0045653,0.005953146,-0.037009216,-0.275107076,-0.062463787,-0.031791646,0.577145867,0.043871836,-0.71042045,0.718634854,0.0198525,-0.014965)
    else:
        STANDARDPLAYERS['Hnst'] = parseTPWeights(0.3,0,0,0,0,0,0,0,0.4,0.2,-0.4,0.85,0,0.02)
        STANDARDPLAYERS['Call'] = parseTPWeights(0.1,0,0,0,0,0,0,0,0.8,-0.8,-0.4,0.3,0,0.02)
        STANDARDPLAYERS['Grdy'] = parseTPWeights(0.8,0,0,0,0,0,0,0,0.6,0.1,-0.2,0.5,0,0.02)

    for name in STANDARDPLAYERS:
        if not name in board:
            w = STANDARDPLAYERS[name]
            addAgent(name,w, board)

if __name__ == "__main__":
    class dud:
        number_of_weights = 18
    IB = Incubator(dud)
    IB.enableStdPlayers()
    def parse():
        parser = ArgumentParser()
        parser.add_argument('-n', '--boardname', help="Name of board", default="evalboard", type=str)
        args = parser.parse_args()
        return args.boardname
    bn = parse()
    #leaderboard = IB.generateLeaderboard(bn, 255)
    leaderboard, gens, players = cacheLeaderboard(bn)
    newBoard, plateauBool, platVal = IB.incubate(leaderboard, 200)
    IB.enableChamps()
    newBoard, plateauBool, platVal = IB.incubate(newBoard, 200)
    IB.enableChamps()
    newBoard, plateauBool, platVal = IB.incubate(newBoard, 200)

    # print("NEWBOARD LEN", len(newBoard))
    # print(plateauBool)
    writeToLeaderboardFile(newBoard, bn+"o", players)
