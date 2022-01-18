##
#  The purpose of this code is to provide a function, parseCaveFromFile(),
#  that reads a cave file from Pikmin 2, and returns a RawCave object filled with information
#  about the cave. This information is very raw, using internal names, and not separating
#  the objects by categories.


import P2CaveParser.constants as constants


## Raw data about a cave.
class RawCave:

    ## Constructor.
    #  @param self Object pointer.
    def __init__(self):
        self.sublevels = []


## Raw data about a cave's sublevel.
class RawSublevel:

    ## Constructor.
    #  @param self Object pointer.
    def __init__(self):
        self.info = RawSublevelInfo()
        self.tekiObjects = []
        self.itemObjects = []
        self.gateObjects = []
        self.capObjects = []


## Raw data about a sublevel's parameters.
class RawSublevelInfo:

    ## Constructor.
    #  @param self Object pointer.
    def __init__(self):
        # Slightly unknown {f000} parameter. Seems to always reflect the sublevel number.
        self.sublevelNumberF000 = None
        # Same as {f000} but it's {f001}.
        self.sublevelNumberF001 = None
        # Ideal max number of objects for objects in the 'main' category.
        self.mainObjectIdealMax = None
        # Ideal max number of objects for objects in the 'treasure' category.
        self.treasureObjectIdealMax = None
        # Ideal max number of gates.
        self.gateObjectIdealMax = None
        # Number of room cave units.
        self.roomUnits = None
        # Ratio between how many corridors and room units there are.
        self.corridorRoomRatio = None
        # Does the sublevel have an exit geyser?
        self.hasGeyser = None
        # Name of the file that lists the cave units to use.
        self.caveUnitListFilename = ''
        # Name of the file that declares the lighting to use.
        self.lightingFilename = ''
        # Name of the skybox to use.
        self.skybox = ''
        # Is the next sublevel hole clogged?
        self.hasClog = None
        # Unknown.
        self.unknownF011 = None
        # Music type. 0 is normal, 1 is boss, 2 is rest.
        self.musicType = None
        # Does the sublevel have an invisible floor plain, or do objects fall into the abyss?
        self.hasFloor = None
        # Maximum number of dead end cave units.
        self.deadEndMax = None
        # If 0, all CapInfo objects are ignored.
        self.hasDeadEndObjects = None
        # Time until the Waterwraith appears.
        self.waterwraithTime = None
        # Unused. If 1, seesaw blocks show up randomly.
        self.hasSeesawBlocks = None


## Raw data about an object entry in a sublevel.
class RawObject:
    
    ## Constructor.
    #  @param self Object pointer.
    def __init__(self):
        # Just the object's class. This uses whatever capitalization is in the file.
        self.objClass = ''
        # Class of the object this enemy is carrying, if any. Again, the capitalization is unchanged.
        self.carrying = None
        # Spawn method. Standard spawn if None, otherwise it's a string with the '$' and the (optional) number.
        self.spawnMethod = None
        # Minimum amount of this entry to spawn.
        self.minAmount = None
        # Random distribution weight.
        self.weight = None
        # Type of spawn point to use.
        self.spawnType = None
        # Type of dead end unit to use, for entries in CapInfo.
        self.capType = None


## Raw data about a gate entry.
class RawGate:
    
    ## Constructor.
    #  @param self Object pointer.
    def __init__(self):
        # Word used to describe this gate. It's always 'gate'.
        self.keyword = ''
        # This gate's health.
        self.health = None
        # Random distribution weight.
        self.weight = None


## Reads a cave file and returns a RawCave object filled with the cave's data.
#  @param infile Input file.
#  @return The parsed cave data.
def parseCaveFromFile(infile):
    caveData = RawCave()
    
    readCaveinfo(infile, caveData)
    
    for s in range(len(caveData.sublevels)):
        readFloorinfo(infile, caveData, s)
        readTekiinfo(infile, caveData, s)
        readIteminfo(infile, caveData, s)
        readGateinfo(infile, caveData, s)
        readCapinfo(infile, caveData, s)
    
    return caveData


## Reads the CaveInfo block in a text file and fills the cave data object.
#  @param infile Input file.
#  @param caveData The RawCave cave data object to fill.
def readCaveinfo(infile, caveData):
    searchingStart = True
    
    for line in infile:
        line = cleanLine(line)
        if len(line) == 0 : continue
        
        if searchingStart:
            if line == '{':
                searchingStart = False
        
        else:
            if line.find('{c000}') != -1:
                sublevelTotal = int(line[9:])
                for s in range(sublevelTotal):
                    caveData.sublevels.append(RawSublevel())
                
            elif line.find('{_eof}') != -1:
                return


## Reads the FloorInfo block in a text file and fills the cave data object.
#  @param infile Input file.
#  @param caveData The RawCave cave data object to fill.
#  @param sublevelNr This sublevel's index number.
def readFloorinfo(infile, caveData, sublevelNr):
    searchingStart = True
    
    for line in infile:
        line = cleanLine(line)
        if len(line) == 0 : continue
        
        if searchingStart:
            if line == '{':
                searchingStart = False
        
        else:
            info = caveData.sublevels[sublevelNr].info
            words = line.split()
            
            if words[0] == '{f000}':
                info.sublevelNumberF000 = int(words[2])
            elif words[0] == '{f001}':
                info.sublevelNumberF001 = int(words[2])
            elif words[0] == '{f002}':
                info.mainObjectIdealMax = int(words[2])
            elif words[0] == '{f003}':
                info.treasureObjectIdealMax = int(words[2])
            elif words[0] == '{f004}':
                info.gateObjectIdealMax = int(words[2])
            elif words[0] == '{f005}':
                info.roomUnits = int(words[2])
            elif words[0] == '{f006}':
                info.corridorRoomRatio = float(words[2])
            elif words[0] == '{f007}':
                info.hasGeyser = int(words[2])
            elif words[0] == '{f008}':
                info.caveUnitListFilename = words[2]
            elif words[0] == '{f009}':
                info.lightingFilename = words[2]
            elif words[0] == '{f00A}':
                info.skybox = words[2]
            elif words[0] == '{f010}':
                info.hasClog = int(words[2])
            elif words[0] == '{f011}':
                info.unknownF011 = words[2]
            elif words[0] == '{f012}':
                info.musicType = int(words[2])
            elif words[0] == '{f013}':
                info.hasFloor = int(words[2])
            elif words[0] == '{f014}':
                info.deadEndMax = int(words[2])
            elif words[0] == '{f015}':
                info.hasDeadEndObjects = int(words[2])
            elif words[0] == '{f016}':
                info.waterwraithTime = float(words[2])
            elif words[0] == '{f017}':
                info.hasSeesawBlocks = int(words[2])
            elif words[0] == '{_eof}':
                return


## Reads the TekiInfo block in a text file and fills the cave data object.
#  @param infile Input file.
#  @param caveData The RawCave cave data object to fill.
#  @param sublevelNr This sublevel's index number.
def readTekiinfo(infile, caveData, sublevelNr):
    searchingStart = True
    searchingCount = True
    nextIsWeight = True
    entryCount = 0
    entryNr = 0
    weightStr = ''
    
    for line in infile:
        line = cleanLine(line)
        if len(line) == 0 : continue
        
        if searchingStart:
            if line == '{':
                searchingStart = False
        
        elif searchingCount:
            entryCount = int(line)
            if entryCount == 0 : return
            for e in range(entryCount):
                caveData.sublevels[sublevelNr].tekiObjects.append(RawObject())
            searchingCount = False
        
        else:
            obj = caveData.sublevels[sublevelNr].tekiObjects[entryNr]
            if nextIsWeight:
                words = line.split()
                
                if words[0][0] == '$':
                    if words[0][1].isdigit():
                        obj.spawnMethod = words[0][0:2]
                        words[0] = words[0][2:]
                    else:
                        obj.spawnMethod = '$'
                        words[0] = words[0][1:]
                
                underscorePos = words[0].find('_')
                if underscorePos == -1:
                    obj.objClass = words[0]
                else:
                    internalNameFound = False
                    tentativeInternalName = words[0][:underscorePos]
                    while underscorePos != -1:
                        if tentativeInternalName.lower() in constants.OBJECTS:
                            internalNameFound = True
                            break
                        else:
                            underscorePos = words[0].find('_', underscorePos + 1)
                            tentativeInternalName = words[0][:underscorePos]
                
                    if internalNameFound and underscorePos != -1:
                        obj.objClass = words[0][:underscorePos]
                        obj.carrying = words[0][underscorePos + 1:]
                    else:
                        obj.objClass = words[0]
                
                weightStr = words[1]
                
                nextIsWeight = False
                
            else:
                obj.spawnType = int(line)
                
                if obj.spawnType == 6:
                    obj.minAmount = int(weightStr)
                else:
                    obj.weight = int(weightStr[-1])
                    weightStr = weightStr[:-1]
                    if len(weightStr) == 0:
                        weightStr = '0'
                    obj.minAmount = int(weightStr)
                
                nextIsWeight = True
                entryNr += 1
            
            if entryNr == entryCount:
                return
            
    
## Reads the ItemInfo block in a text file and fills the cave data object.
#  @param infile Input file.
#  @param caveData The RawCave cave data object to fill.
#  @param sublevelNr This sublevel's index number.
def readIteminfo(infile, caveData, sublevelNr):
    searchingStart = True
    searchingCount = True
    entryCount = 0
    entryNr = 0
    
    for line in infile:
        line = cleanLine(line)
        if len(line) == 0 : continue
        
        if searchingStart:
            if line == '{':
                searchingStart = False
        
        elif searchingCount:
            entryCount = int(line)
            if entryCount == 0 : return
            for e in range(entryCount):
                caveData.sublevels[sublevelNr].itemObjects.append(RawObject())
            searchingCount = False
        
        else:
            obj = caveData.sublevels[sublevelNr].itemObjects[entryNr]
            words = line.split()
            
            obj.objClass = words[0]
            obj.weight = int(words[1][-1])
            s = words[1][:-1]
            if len(s) == 0:
                s = '0'
            obj.minAmount = int(s)
            
            entryNr += 1
            
            if entryNr == entryCount:
                return


## Reads the GateInfo block in a text file and fills the cave data object.
#  @param infile Input file.
#  @param caveData The RawCave cave data object to fill.
#  @param sublevelNr This sublevel's index number.
def readGateinfo(infile, caveData, sublevelNr):
    searchingStart = True
    searchingCount = True
    nextIsHealth = True
    entryCount = 0
    entryNr = 0
    
    for line in infile:
        line = cleanLine(line)
        if len(line) == 0 : continue
        
        if searchingStart:
            if line == '{':
                searchingStart = False
        
        elif searchingCount:
            entryCount = int(line)
            if entryCount == 0 : return
            for e in range(entryCount):
                caveData.sublevels[sublevelNr].gateObjects.append(RawGate())
            searchingCount = False
        
        else:
            obj = caveData.sublevels[sublevelNr].gateObjects[entryNr]
            if nextIsHealth:
                words = line.split()
                
                obj.keyword = words[0]
                obj.health = float(words[1])
                
                nextIsHealth = False
                
            else:
                obj.weight = int(line[-1])
                
                nextIsHealth = True
                entryNr += 1
            
            if entryNr == entryCount:
                return


## Reads the CapInfo block in a text file and fills the cave data object.
#  @param infile Input file.
#  @param caveData The RawCave cave data object to fill.
#  @param sublevelNr This sublevel's index number.
def readCapinfo(infile, caveData, sublevelNr):
    searchingStart = True
    searchingCount = True
    nextIsCapType = True
    nextIsWeight = False
    entryCount = 0
    entryNr = 0
    weightStr = ''
    
    for line in infile:
        line = cleanLine(line)
        if len(line) == 0 : continue
        
        if searchingStart:
            if line == '{':
                searchingStart = False
        
        elif searchingCount:
            entryCount = int(line)
            if entryCount == 0 : return
            for e in range(entryCount):
                caveData.sublevels[sublevelNr].capObjects.append(RawObject())
            searchingCount = False
        
        else:
            obj = caveData.sublevels[sublevelNr].capObjects[entryNr]
            if nextIsCapType:
                obj.capType = int(line)
                
                nextIsCapType = False
                nextIsWeight = True
                
            elif nextIsWeight:
                words = line.split()
                
                if words[0][0] == '$':
                    if words[0][1].isdigit():
                        obj.spawnMethod = words[0][0:1]
                        words[0] = words[0][2:]
                    else:
                        obj.spawnMethod = 1
                        words[0] = words[0][1:]
                
                underscorePos = words[0].find('_')
                if underscorePos == -1:
                    obj.objClass = words[0]
                else:
                    internalNameFound = False
                    tentativeInternalName = words[0][:underscorePos]
                    while underscorePos != -1:
                        if tentativeInternalName.lower() in constants.OBJECTS:
                            internalNameFound = True
                            break
                        else:
                            underscorePos = words[0].find('_', underscorePos + 1)
                            tentativeInternalName = words[0][:underscorePos]
                
                    if internalNameFound and underscorePos != -1:
                        obj.objClass = words[0][:underscorePos]
                        obj.carrying = words[0][underscorePos + 1:]
                    else:
                        obj.objClass = words[0]
                
                weightStr = words[1]
                
                nextIsCapType = False
                nextIsWeight = False
                
            else:
                obj.spawnType = int(line)
                
                obj.weight = int(weightStr[-1])
                weightStr = weightStr[:-1]
                if len(weightStr) == 0:
                    weightStr = '0'
                obj.minAmount = int(weightStr)
                
                nextIsCapType = True
                nextIsWeight = False
                entryNr += 1
            
            if entryNr == entryCount:
                return


## Cleans a line, removing its comments and indentation.
#  @param line Line of text to clean.
#  @return The cleaned line.
def cleanLine(line):
    numberSignPos = line.find('#')
    
    if numberSignPos != -1:
        line = line[0:numberSignPos]
    
    line = line.strip(' \t\r\n')
    
    return line
