import csv
import os
import random

def writeToFile(filename, *data):
    contentToWrite = data[0]
    with open(folderize(filename), mode='w') as outputFile:
        myWriter = csv.writer(outputFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in contentToWrite:
            # Debug print for raw info read from csv file
            #print("Row: ", row)
            myWriter.writerow(row)
        outputFile.close()

def readFileAndGetData(filename):
    with open(folderize(filename)) as csvFile:
        csvReader = csv.reader(csvFile, delimiter= ',')
        line = 0
        data = []
        for row in csvReader:
            parsedRow = []
            if line == 0:
                for e in row:
                    if len(e) > 0:
                        parsedRow.append(float(e))
                    else:
                        parsedRow.append(e)
                data.append(parsedRow)
            else:
                data.append(row)
            line += 1
        #print('\nProcessed '+ str(line) +' lines\n')
        csvFile.close()
        return data

# Returns the leaderboard
def getLeaderboard(filename):
    with open(folderize(filename), mode='r') as readFile:
        csvReader = csv.reader(readFile, delimiter = ",")
        leaderboard = list(csvReader)
        readFile.close()
        return leaderboard

# References the folder and file extension
def folderize(filename):
    return os.getcwd()+"/player-seeds/" + filename + ".csv"
