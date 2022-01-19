##
#  The purpose of this code is to provide a function, clean_parsed_cave(),
#  that reads a Cave object read from parse_cave_from_file(), and outputs a
#  P2Cave object, with user-friendly information, and helper functions.
#  Special thanks to JHawk for his research in the sublevel generation algorithm.


import P2CaveParser.constants as constants


CAT_MAIN = 0
CAT_DECORATIVE = 1
CAT_DEAD_END = 2
CAT_TREASURE = 3
CAT_GATE = 4


## Clean data about a cave.
class P2Cave:
    
    ## Constructor.
    #  @param self Object pointer.
    def __init__(self):
        # Name of the text file with the cave data.
        self.internalName = ''
        # Info about all sublevels.
        self.sublevels = []
    
    ## Builds information using a RawCave object.
    #  @param self Object pointer.
    #  @param raw The raw cave object.
    def fromRaw(self, raw):
        for s in range(len(raw.sublevels)):
            self.sublevels.append(P2Sublevel())
            self.sublevels[s].fromRaw(raw.sublevels[s])
            self.sublevels[s].number = s + 1


## Clean data about a cave's sublevel.
class P2Sublevel:
    
    ## Constructor.
    #  @param self Object pointer.
    def __init__(self):
        # Information about the sublevel.
        self.info = P2SublevelInfo()
        # Full list of all entries that can or will spawn objects.
        self.allEntries = []
        # List of all object entries that are being carried by others.
        self.carriedObjects = []


    ## Builds information using a RawSublevel object.
    #  @param self Object pointer.
    #  @param raw The raw sublevel object.
    def fromRaw(self, raw):
        self.info.fromRaw(raw.info)

        curEntryId = 1

        # First, fill in the list of all object entries.
        for teki in raw.tekiObjects:
            e = P2SublevelEntry()
            e.fromRawObject(teki)
            e.id = curEntryId
            if teki.spawnType == 6:
                e.category = CAT_DECORATIVE
            else:
                e.category = CAT_MAIN
            self.allEntries.append(e)
            curEntryId += 1
        
        for item in raw.itemObjects:
            e = P2SublevelEntry()
            e.fromRawObject(item)
            e.id = curEntryId
            e.category = CAT_TREASURE
            self.allEntries.append(e)
            curEntryId += 1
        
        for gate in raw.gateObjects:
            e = P2SublevelEntry()
            e.fromRawGate(gate)
            e.id = curEntryId
            e.category = CAT_GATE
            self.allEntries.append(e)
            curEntryId += 1
        
        for cap in raw.capObjects:
            e = P2SublevelEntry()
            e.fromRawObject(cap)
            e.id = curEntryId
            e.category = CAT_DEAD_END
            self.allEntries.append(e)
            curEntryId += 1

        # Now assign everything that's being carried by everything else.
        for e in self.allEntries:
            if e.carryingClass is not None:
                o = P2SublevelEntry()
                o.id = curEntryId
                o.objClass = e.carryingClass
                o.minAmount = 1
                o.weight = 0
                o.carriedBy = e.id
                self.info.treasureObjectMinTotal += o.minAmount
                self.allEntries.append(o)
                self.carriedObjects.append(o)
                curEntryId += 1
        
        # Update the sums of minimum amounts and weights.
        for e in self.allEntries:
            if e.category == CAT_MAIN:
                self.info.mainObjectMinTotal += e.minAmount
                self.info.mainObjectWeightsSum += e.weight
            elif e.category == CAT_TREASURE:
                self.info.treasureObjectMinTotal += e.minAmount
                self.info.treasureObjectWeightsSum += e.weight
            elif e.category == CAT_GATE:
                self.info.gateObjectMinTotal += e.minAmount
                self.info.gateObjectWeightsSum += e.weight


## Clean data about a sublevel's info.
class P2SublevelInfo:
    
    ## Constructor.
    #  @param self Object pointer.
    def __init__(self):
        # This sublevel's number. Starts at 1.
        self.number = None
        # Ideal max number of objects for objects in the 'main' category. (Parameter {f002}.)
        self.mainObjectIdealMax = None
        # Ideal max number of objects for objects in the 'treasure' category. (Parameter {f003}.)
        self.treasureObjectIdealMax = None
        # Ideal max number of gates. (Parameter {f004}.)
        self.gateObjectIdealMax = None
        # Number of room cave units. (Parameter {f005}.)
        self.roomUnits = None
        # Ratio between how many corridors and room units there are. (Parameter {f006}.)
        self.corridorRoomRatio = None
        # Does the sublevel have an exit geyser? (Parameter {f007}.)
        self.hasGeyser = None
        # Name of the file that lists the cave units to use. (Parameter {f008}.)
        self.caveUnitListFilename = None
        # Name of the file that declares the lighting to use. (Parameter {f009}.)
        self.lightingFilename = None
        # Name of the skybox to use. (Parameter {f00A}.)
        self.skybox = None
        # Is the next sublevel hole clogged? (Parameter {f010}.)
        self.hasClog = None
        # Music type. 0 is normal, 1 is boss, 2 is rest. (Parameter {f012}.)
        self.musicType = None
        # Does the sublevel have an invisible floor plane, or do objects fall into the abyss? (Parameter {f013}.)
        self.hasFloor = None
        # 0-100 chance of an open doorway being a dead end. (Parameter {f014}.)
        self.deadEndChance = None
        # TODO: do something with this
        # File format version. If 0, all CapInfo objects are ignored. (Parameter {f015}.)
        self.fileFormat = None
        # Time until the Waterwraith appears. (Parameter {f016}.)
        self.waterwraithTime = None
        # If 1, seesaw blocks show up randomly. Unused. (Parameter {f017}.)
        self.hasSeesawBlocks = None
        # Minimum number of 'main' category objects that will spawn.
        self.mainObjectMinTotal = 0
        # Minimum number of 'treasure' category objects that will spawn.
        self.treasureObjectMinTotal = 0
        # Minimum number of 'gate' category objects that will spawn.
        self.gateObjectMinTotal = 0
        # Total sum of the weights of 'main' category objects.
        self.mainObjectWeightsSum = 0
        # Total sum of the weights of 'treasure' category objects.
        self.treasureObjectWeightsSum = 0
        # Total sum of the weights of 'gate' category objects.
        self.gateObjectWeightsSum = 0
        
    
    ## Builds information using a RawSublevelInfo object.
    #  @param self Object pointer.
    #  @param raw The raw sublevel info object.
    def fromRaw(self, raw):
        self.number = raw.sublevelNumberF000 + 1
        self.mainObjectIdealMax = raw.mainObjectIdealMax
        self.treasureObjectIdealMax = raw.treasureObjectIdealMax
        self.gateObjectIdealMax = raw.gateObjectIdealMax
        self.roomUnits = raw.roomUnits
        self.corridorRoomRatio = raw.corridorRoomRatio
        self.hasGeyser = raw.hasGeyser
        self.caveUnitListFilename = raw.caveUnitListFilename
        self.lightingFilename = raw.lightingFilename
        self.skybox = raw.skybox
        self.hasClog = raw.hasClog
        self.musicType = raw.musicType
        self.hasFloor = raw.hasFloor
        self.deadEndChance = raw.deadEndChance
        self.fileFormat = raw.fileFormat
        self.waterwraithTime = raw.waterwraithTime
        self.hasSeesawBlocks = raw.hasSeesawBlocks


## Clean data about an object entry in a sublevel.
class P2SublevelEntry:

    ## Constructor.
    #  @param self Object pointer.
    def __init__(self):
        # Entry numeric ID. Doesn't reflect anything in-game, but exists for ease of use.
        self.id = None
        # Object's class. This is the internal name.
        self.objClass = None
        # Object's category. Use OBJ_CAT_*.
        self.category = None
        # Class name of the object it is carrying, if any.
        self.carryingClass = None
        # ID of the object it is carrying, if any.
        self.carrying = None
        # ID of the object that is carrying it, if any.
        self.carriedBy = None
        # Spawn method. Standard spawn if None, otherwise it's a string with the '$' and the (optional) number.
        self.spawnMethod = None
        # Minimum amount the game wants to spawn.
        self.minAmount = None
        # Random chance weight.
        self.weight = None
        # Spawn type. This is a number.
        self.spawnType = None
        # Health, if it's a gate.
        self.gateHealth = None
        # Gate keyword, if it's a gate.
        self.gateKeyword = None
        # Type of dead end unit to use, for entries in CapInfo.
        self.capType = None
    

    ## Builds information using a RawObject object.
    #  Not all information will be filled, since some will depend
    #  on the sublevel data.
    #  @param self Object pointer.
    #  @param raw The raw object info object.
    def fromRawObject(self, raw):
        self.objClass = raw.objClass
        self.carryingClass = raw.carrying
        self.spawnMethod = raw.spawnMethod
        self.minAmount = raw.minAmount
        self.weight = raw.weight
        self.spawnType = raw.spawnType
        self.capType = raw.capType
    
    
    ## Builds information using a RawGate object.
    #  Not all information will be filled, since some will depend
    #  on the sublevel data.
    #  @param self Object pointer.
    #  @param raw The raw gate info object.
    def fromRawGate(self, raw):
        self.category = CAT_GATE
        self.minAmount = raw.minAmount
        self.weight = raw.weight
        self.gateHealth = raw.health
        self.gateKeyword = raw.keyword
