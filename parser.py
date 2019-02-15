import time
import re
import json
import os

fileTime = ""

inCombat = False

target = ""
meleeDmg = 0
nonMeleeDmg = 0
newDMG = 0
dmgHistory = []
regexDict = {}
found = ""

# Load config and initialize variables 
def loadConfig():
    global config, regexDict, items
    index = 0
    print ("Loading configuration and setting variables...")
    with open('config.json') as jsonData:
        config = json.load(jsonData)

    for key, value in config["regexDict"].items():
        reg = r""+value
        regexDict[key] = reg

    for item in config["items"]:
        index += 1
        if index == 1:
            regexDict["AUC"] = r"("

        regexDict["AUC"] += item

        if index < len(config["items"]):
            regexDict["AUC"] += "|"

        if index == len(config["items"]):
            regexDict["AUC"] += ")"
    
# <summary>Reads file</summary>
# <param name="file">The file path</param>
# <returns>lines of a file</returns>
def readFile(file):
    file.seek(0,2)
    global fileTime
    lastTime = ""
    while True:
        # Monitor config.json for changes
        fileTime = os.stat("config.json").st_mtime
        if (lastTime != fileTime and lastTime != ""):
            loadConfig()

        lastTime = fileTime

        line = file.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line

# <summary>Reads line from file with a regex</summary>
# <param name="regex">String to load a regex</param>
# <param name="line">Line from file being parsed</param>
# <returns>boolean</returns> 
def regexMatch(regex, line):
    matches = re.finditer(regexDict[regex], line,  re.MULTILINE | re.IGNORECASE)
    global target, newDMG, nonMeleeDmg, meleeDmg, found

    for matchNum, match in enumerate(matches, start=1):
    
        # Conditional area for matches
        # print ("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
        for groupNum in range(0, len(match.groups())):
            groupNum = groupNum + 1
            
            # Conditional area for groups
            # print ("MatchNum {matchNum} Group {groupNum} found at {start}-{end}: {group}".format(matchNum = matchNum,groupNum = groupNum, start = match.start(groupNum), end = match.end(groupNum), group = match.group(groupNum)))
            if (regex == "meleeYDMG" or regex == "dotYDMG"):
                if (groupNum == 2):
                    target = match.group(groupNum)
                if (groupNum == 3):
                    newDMG = match.group(groupNum)
                    global meleeDmg, nonMeleeDmg
                    if regex == "dotYDMG":
                        nonMeleeDmg += int(newDMG)
                    if regex == "meleeYDMG":
                        meleeDmg += int(newDMG)                        
                    print ("Attacking {target} total damage done => Melee: {meleeDmg}, NonMelee: {nonMeleeDmg}".format(target = target, meleeDmg = meleeDmg, nonMeleeDmg = nonMeleeDmg))
            if (regex == "AUC"):
                found = match.group(1)
        return True

# <summary>Sets isCombat True</summary>
def startCombat():
    print ("Start Combat")
    global inCombat
    inCombat = True

# <summary>Sets isCombat false, adds past fight to histroy, and resets variables</summary>
def endCombat():
    print ("End of Combat")
    global inCombat, target, meleeDmg, nonMeleeDmg
    inCombat = False
    dmgHistory.append({"target": target, "meleeDmg": meleeDmg, "nonMeleeDmg": nonMeleeDmg, "totalDmg": meleeDmg + nonMeleeDmg})
    meleeDmg = 0 
    nonMeleeDmg = 0 
    target = ""
    print(dmgHistory)

# <summary>Adds meleeDmg while isCombat</summary>
def combat():
    regexMatch("meleeYDMG", line)
    regexMatch("dotYDMG", line)

# <summary>Adds meleeDmg while isCombat</summary>
def auctionSeeker():
    if (regexMatch("AUC", line)):
        print (found)



# <summary>Main loop</summary>
if __name__ == '__main__':
    loadConfig()
    logfile = open(config["filePath"] + config["file"],"r")
    loglines = readFile(logfile)

    for line in loglines:
        auctionSeeker()
        if (regexMatch("EOC", line)):
           endCombat()
        if (regexMatch("SOC", line)):
           startCombat()
        if (inCombat):
            combat()
            