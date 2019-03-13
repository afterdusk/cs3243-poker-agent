import csv
import random
from test_arena import trainBots
from trainable_player import folderize
from trainable_player import MASTERFILE

def getBoard():
    with open(folderize(MASTERFILE), mode='r') as readFile:
        csvReader = csv.reader(readFile, delimiter = ",")
        leaderboard = list(csvReader)
        readFile.close()
        return leaderboard

def arrangeMatch(bot_1, bot_2, iterations):
    num_games = 4
    num_rounds = 101
    print("\n============Match number " + str(iterations) +"============")
    return trainBots(bot_1, bot_2, num_games, num_rounds)

def getBotsFromBoard():
    leaderboard = getBoard()
    #print(leaderboard)
    numberOfBots = len(leaderboard) - 1
    first = random.randint(1,numberOfBots)
    second = random.randint(1,numberOfBots)
    while second == first:
        second = random.randint(1,numberOfBots)
    return (leaderboard[first][0],leaderboard[second][0])

def beginTrainingAllBots(cycles):
    iterations = 0
    while iterations < cycles:
        bots = getBotsFromBoard()
        arrangeMatch(bots[0], bots[1], iterations)
        iterations += 1

def trainNamedBot(botName):
    board = getBoard()
    iterations = 0
    oppIndex = 1
    for row in board:
        opponent = board[oppIndex][0]
        if opponent == botName:
            oppIndex += 1
            if oppIndex < len(board):
                opponent = board[oppIndex][0]
            else:
                break
        deadbot = arrangeMatch(botName,opponent, iterations)
        if len(deadbot) > 1:
            return False
        oppIndex += 1
        if oppIndex >= len(board):
            break
        iterations += 1
    return True

def roundRobinTraining():
    print("ROUND ROBIN TRAINING")
    board = getBoard()
    botlist = []
    for row in board[0:]:
        botlist.append(row[0])
    line = 0
    for bot in botlist:
        if line == 0:
            line += 1
            continue
        alive = trainNamedBot(bot)
        if not alive:
            break
        line += 1

def clearAllHistories():
    # Sets all loacl win-loss-performace histories of bots to 0,0
    board = getBoard()
    boardLine = 0
    for row in board:
        if boardLine == 0:
            boardLine = 1
            continue
        target = row[0]
        with open(folderize(target)) as readFile:
            csvReader = csv.reader(readFile,  delimiter= ',')
            line = 0
            newContents = []
            for row in csvReader:
                if line == 1:
                    newContents.append((0,0,0))
                else:
                    newContents.append(row)
                line += 1
        readFile.close()

        with open(folderize(target), mode='w') as writeFile:
            writer = csv.writer(writeFile)
            writer.writerows(newContents)
        writeFile.close()


clearAllHistories()
#beginTrainingAllBots(1500)
i = 0
while i < 50:
    roundRobinTraining()
    print("/n/n%%%%%%%%%%%%%%%%%%%%%% Finished Round Robin round " + str(i+1) +"%%%%%%%%%%%%%%%%%%%%%%/n/n")
    i += 1
