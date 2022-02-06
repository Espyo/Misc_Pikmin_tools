##
#  This tool grabs data from a Pikmin 2 cave, and outputs some wikitext,
#  representing the cave's objects, so that it can be uploaded to Pikipedia.
#  If it finds a scenario that's too difficult to implement via scripting,
#  or just plain unexpected, it outputs an error to STDOUT so that a
#  human being can manually tweak it.

'''
#TODO
Current task:
* Grab random sublevels, try to parse them by hand, and see if this script matches up


Next tasks?:
* Support for multiple regions/versions
* * Maybe just support US and then the other changes can be made manually
* Standardize the treasure names on the wiki
'''

from email import header
import io, os, sys
import P2CaveParser.p2CaveParser as p2cp
import P2CaveParser.p2CaveParserCleaner as p2cpc
import P2CaveParser.constants as constants

## 
#  Main function.
#  @return -1 in case no argument's been output. 0 on success.
def main():
    if len(sys.argv) < 2:
        print('Pikmin 2 cave object dumper, by Espyo')
        print('Usage: {0} <input file> [<output file>]'.format(sys.argv[0]))
        print('')
        print('This tool can analyse a Pikmin 2 cave and write exactly how the')
        print('objects are distributed per floor, in a format convenient')
        print('for adding the information to Pikipedia.')
        return -1

    inputFn = sys.argv[1]
    outputFn = 'dump.txt'
    
    if len(sys.argv) >= 3:
        outputFn = sys.argv[2]
    
    doDump(inputFn, outputFn)

    return 0


##
#  Start the dumping process.
#  @param inputFn Input filename.
#  @param outputFn Output filename.
def doDump(inputFn, outputFn):
    inFile = open(inputFn, 'r', errors='ignore')
    outFile = io.open(outputFn, 'w')
    
    caveRaw = p2cp.parseCaveFromFile(inFile)
    cave = p2cpc.P2Cave()
    cave.fromRaw(caveRaw)
    _, caveFn = os.path.split(inputFn)
    cave.internalName = caveFn[:-4]
    if cave.internalName[:3] == 'ch_':
        cave.caveType = p2cpc.CAVE_TYPE_CHALLENGE
    elif cave.internalName[:3] == 'vs_':
        cave.caveType = p2cpc.CAVE_TYPE_BATTLE
    else:
        cave.caveType = p2cpc.CAVE_TYPE_STORY
    preProcessCave(cave)
    
    for s in cave.sublevels:
        outFile.write('-------- Sublevel {0} --------\n'.format(s.number))
        outFile.write(getSimpleWikiList(cave, s.number - 1))
        outFile.write('\n')
        outFile.write('\n')
        outFile.write(getDetailedWikiList(cave, s.number - 1))
        outFile.write('\n\n')
    
    print('Finished dumping into "{0}".'.format(outputFn))
    
    inFile.close()
    outFile.close()


##
#  Does some pre-processing to the cave, like adding some wiki-helpful info
#  to the existing cave sublevel entry objects.
#  @param cave Cave object to process.
def preProcessCave(cave):
    
    curSublevelNr = 1

    for s in cave.sublevels:

        # Create entries for the Titan Dweevil weapon treasures.
        for e in s.allEntries:
            if e.objClass is not None and e.objClass == 'bigtreasure':
                o = p2cpc.P2SublevelEntry()
                o.id = len(s.allEntries) + 1
                o.objClass = 'gas'
                o.minAmount = 1
                o.weight = 0
                o.carriedBy = e.id
                s.allEntries.append(o)

                o = p2cpc.P2SublevelEntry()
                o.id = len(s.allEntries) + 1
                o.objClass = 'elec'
                o.minAmount = 1
                o.weight = 0
                o.carriedBy = e.id
                s.allEntries.append(o)

                o = p2cpc.P2SublevelEntry()
                o.id = len(s.allEntries) + 1
                o.objClass = 'water'
                o.minAmount = 1
                o.weight = 0
                o.carriedBy = e.id
                s.allEntries.append(o)

                o = p2cpc.P2SublevelEntry()
                o.id = len(s.allEntries) + 1
                o.objClass = 'fire'
                o.minAmount = 1
                o.weight = 0
                o.carriedBy = e.id
                s.allEntries.append(o)

                o = p2cpc.P2SublevelEntry()
                o.id = len(s.allEntries) + 1
                o.objClass = 'loozy'
                o.minAmount = 1
                o.weight = 0
                o.carriedBy = e.id
                s.allEntries.append(o)
        
        # Give everything a wiki name, type, and disambig.
        for e in s.allEntries:
            try:
                if e.objClass is None:
                    if e.category == p2cpc.CAT_GATE:
                        e.wikiName = 'Gate'
                        e.wikiType = 'gat'
                        e.wikiDisambig = ''
                    continue
                data = constants.OBJECTS[e.objClass]
                e.wikiName = data[0]
                e.wikiType = data[1]
                e.wikiDisambig = data[2]
            except KeyError:
                printSublevelError(curSublevelNr, 'UNKNOWN ENTRY OBJECT CLASS {0}.'.format(e.objClass))
                e.wikiName = 'UNKNOWN!{0}'.format(e.objClass)
                e.wikiType = 'ene'
                e.wikiDisambig = ''
        
        # Find some unsupported scenarios.
        nGateObjects = 0
        for e in s.allEntries:
            if e.category == p2cpc.CAT_GATE:
                nGateObjects += 1
                if e.weight == 0:
                    printSublevelError(curSublevelNr, 'GATE WITH 0 WEIGHT FOUND! UNSUPPORTED SCENARIO.')
                if e.minAmount != 0:
                    printSublevelError(curSublevelNr, 'GATE WITH {0} MIN AMOUNT FOUND! UNSUPPORTED SCENARIO.'.format(e.minAmount))

        if s.info.mainObjectMinTotal == 0 and s.info.treasureObjectMinTotal == 0:
            printSublevelError(curSublevelNr, 'THERE ARE NO MINIMUM OBJECTS TO SPAWN. THE DETAILED OBJECT LIST MIGHT LOOK WEIRD WITH AN EMPTY FIRST SECTION. UNSUPPORTED SCENARIO.')

        # Find some weird scenarios that might be worth pointing out or something.
        if s.info.mainObjectMinTotal >= s.info.mainObjectIdealMax and s.info.mainObjectWeightsSum > 0:
            printSublevelError(curSublevelNr, 'Note: There is no filler room in the main category, but there are main category entries with weight.')
        if s.info.treasureObjectMinTotal >= s.info.treasureObjectIdealMax and s.info.treasureObjectWeightsSum > 0:
            printSublevelError(curSublevelNr, 'Note: There is no filler room in the treasure category, but there are treasure category entries with weight.')
        if s.info.gateObjectMinTotal >= s.info.gateObjectIdealMax and s.info.gateObjectWeightsSum > 0:
            printSublevelError(curSublevelNr, 'Note: There is no filler room in the gate category, but there are gate category entries with weight.')
        
        if s.info.mainObjectMinTotal < s.info.mainObjectIdealMax and s.info.mainObjectWeightsSum == 0:
            printSublevelError(curSublevelNr, 'Note: There is filler room in the main category, but no main category entries with weight.')
        if s.info.treasureObjectMinTotal < s.info.treasureObjectIdealMax and s.info.treasureObjectWeightsSum == 0:
            printSublevelError(curSublevelNr, 'Note: There is filler room in the treasure category, but no treasure category entries with weight.')
        if s.info.gateObjectMinTotal < s.info.gateObjectIdealMax and s.info.gateObjectWeightsSum == 0:
            printSublevelError(curSublevelNr, 'Note: There is filler room in the gate category, but no gate category entries with weight.')
        
        if s.info.mainObjectMinTotal > s.info.mainObjectIdealMax:
            printSublevelError(curSublevelNr, 'Note: There are more minimum objects in the main category than the ideal main category max.')
        if s.info.treasureObjectMinTotal > s.info.treasureObjectIdealMax:
            printSublevelError(curSublevelNr, 'Note: There are more minimum objects in the treasure category than the ideal treasure category max.')
        if s.info.gateObjectMinTotal > s.info.gateObjectIdealMax:
            printSublevelError(curSublevelNr, 'Note: There are more minimum objects in the gate category than the ideal gate category max.')

        if s.info.gateObjectIdealMax == 0 and nGateObjects > 0:
            printSublevelError(curSublevelNr, 'Note: {0} gates found, but the sublevel\'s gate object ideal max is 0.'.format(nGateObjects))
        
        curSublevelNr += 1


##
#  Given a cave object, it returns a simple list of the objects
#  in the specified sublevel index, ready for wiki use.
#  @param cave Cave object.
#  @param sublevelNr Sublevel number, starting at 0.
#  @return The list.
def getSimpleWikiList(cave, sublevelNr):

    sublevel = cave.sublevels[sublevelNr]
    
    # Process treasures.
    treasureMap = {}
    for e in sublevel.allEntries:
        if e.wikiType == 'tre':
            treasureMap[e.objClass] = lambda: None # Empty object.
            treasureMap[e.objClass].carriedBy = e.carriedBy

    for t in treasureMap:
        treasureMap[t].min = sublevel.getClassMinimumSpawns(t)
        treasureMap[t].max = sublevel.getClassMaximumSpawns(t)
        if sublevel.doesTreasureHaveMixedCarrying(t):
            printSublevelError(sublevelNr + 1, 'TREASURE {0} HAS MIXED CARRYING INFORMATION! UNSUPPORTED SCENARIO.'.format(t))
        if treasureMap[t].min == 0:
            printSublevelError(sublevelNr + 1, 'TREASURE {0} APPEARS A TOTAL OF 0 TIMES! UNSUPPORTED SCENARIO.'.format(t))
        if treasureMap[t].carriedBy is not None and \
            sublevel.allEntries[treasureMap[t].carriedBy - 1].weight is not None and \
            sublevel.allEntries[treasureMap[t].carriedBy - 1].weight > 0:
            printSublevelError(sublevelNr + 1, 'TREASURE {0} IS INSIDE AN ENEMY WITH WEIGHT! UNSUPPORTED SCENARIO.'.format(t))
    
    # Process enemies.
    enemyMap = {}
    for e in sublevel.allEntries:
        if e.wikiType == 'ene':
            enemyMap[e.objClass] = lambda: None # Empty object.
    
    for e in enemyMap:
        enemyMap[e].min = sublevel.getClassMinimumSpawns(e)
        enemyMap[e].max = sublevel.getClassMaximumSpawns(e)
    
    # Process obstacles.
    obstacleMap = {}
    for e in sublevel.allEntries:
        if e.wikiType == 'obs':
            obstacleMap[e.objClass] = lambda: None # Empty object.
    
    for o in obstacleMap:
        obstacleMap[o].min = sublevel.getClassMinimumSpawns(o)
        obstacleMap[o].max = sublevel.getClassMaximumSpawns(o)
    
    # Process vegetation.
    vegetationMap = {}
    for e in sublevel.allEntries:
        if e.wikiType == 'pla':
            vegetationMap[e.objClass] = lambda: None # Empty object.
    
    for v in vegetationMap:
        vegetationMap[v].min = sublevel.getClassMinimumSpawns(v)
        vegetationMap[v].max = sublevel.getClassMaximumSpawns(v)
    
    # Process gates and others.
    gateEntries = []
    otherMap = {}
    for e in sublevel.allEntries:
        if e.category == p2cpc.CAT_GATE:
            gateEntries.append(e)
        if e.wikiType == 'oth':
            otherMap[e.objClass] = lambda: None # Empty object.
    
    for o in otherMap:
        otherMap[o].min = sublevel.getClassMinimumSpawns(o)
        otherMap[o].max = sublevel.getClassMaximumSpawns(o)

    # Process Mitites.
    maxMitites = 0
    mititeSourceName = ''
    nMititeSources = 0
    if 'egg' in otherMap:
        maxMitites = otherMap['egg'].max
        mititeSourceName = 'from eggs'
        nMititeSources += 1
    if 'qurione' in enemyMap:
        maxMitites = enemyMap['qurione'].max
        mititeSourceName = 'from Honeywisps'
        nMititeSources += 1
    if 'bigfoot' in enemyMap:
        maxMitites = enemyMap['bigfoot'].max * 3
        mititeSourceName = 'inside the Raging Long Legs'
        nMititeSources += 1
    if nMititeSources > 1:
        printSublevelError(sublevelNr + 1, 'THERE ARE DIFFERENT MITITE SOURCES! CAN\'T FIGURE OUT THE NUMBER OF MITITES. UNSUPPORTED SCENARIO.')
    
    # Write treasures.
    lines = []
    result = '* \'\'\'Treasures\'\'\':\n'
    if len(treasureMap) == 0:
        result += '** None\n'
    else:
        for t in treasureMap:
            l = '** {0}'.format(getIconAndName(t))
            if cave.caveType != p2cpc.CAVE_TYPE_STORY:
                l += ' &times; {0}'.format(getTimes(treasureMap[t].min, treasureMap[t].max))
            if treasureMap[t].carriedBy is not None:
                carrier = sublevel.allEntries[treasureMap[t].carriedBy - 1]
                l += ' (inside {0})'.format(plural(carrier.wikiName, treasureMap[t].min))
            if constants.OBJECTS[t][3] == 'p':
                l += ' (partially buried)'
            elif constants.OBJECTS[t][3] == 'f':
                l += ' (fully buried)'
            if constants.OBJECTS[t][4] == 'r':
                l += ' \'\'\'!!!!!!!!TODO: ADD OTHER REGIONS!!!!!!!!\'\'\''
            lines.append(l)
        result = appendSortedLines(lines, result)
    
    # Write enemies.
    lines = []
    result += '* \'\'\'Enemies\'\'\':\n'
    if len(enemyMap) == 0 and maxMitites == 0:
        result += '** None\n'
    else:
        for e in enemyMap:
            l = '** {0} &times; {1}'.format(getIconAndName(e), getTimes(enemyMap[e].min, enemyMap[e].max))
            lines.append(l)
        result = appendSortedLines(lines, result)
    
    if maxMitites is None or maxMitites > 0:
        result += '** {{{{icon|Mitite|y}}}} (group of 10) &times; {0} ({1})\n'.format(getTimes(0, maxMitites), mititeSourceName)
    
    # Write obstacles.
    lines = []
    result += '* \'\'\'Obstacles\'\'\':\n'
    if len(obstacleMap) == 0:
        result += '** None\n'
    else:
        for o in obstacleMap:
            l = '** {0} &times; {1}'.format(getIconAndName(o), getTimes(obstacleMap[o].min, obstacleMap[o].max))
            lines.append(l)
        result = appendSortedLines(lines, result)
    
    # Write vegetation.
    lines = []
    result += '* \'\'\'Vegetation\'\'\':\n'
    if len(vegetationMap) == 0:
        result += '** None\n'
    else:
        for v in vegetationMap:
            l = '** {0} &times; {1}'.format(getIconAndName(v), getTimes(vegetationMap[v].min, vegetationMap[v].max))
            if v == 'blackpom' or v == 'whitepom':
                if (cave.internalName + ' ' + str(sublevelNr + 1)) in constants.MAX_REQ_CANDYPOPS:
                    l += ' (if [[Candypop family#Maximum Pikmin requirement|max Pikmin requirement]] is met)'
            lines.append(l)
        result = appendSortedLines(lines, result)
    
    # Write gates and others.
    lines = []
    result += '* \'\'\'Others\'\'\':\n'
    if len(otherMap) == 0 and len(gateEntries) == 0:
        result += '** None\n'
    else:
        for o in otherMap:
            l = '** {0} &times; {1}'.format(getIconAndName(o), getTimes(otherMap[o].min, otherMap[o].max))
            lines.append(l)
        for g in gateEntries:
            l = '** [[Gate]] with {0:.0f} [[Health|HP]] &times; '.format(g.gateHealth)
            if len(gateEntries) == 1:
                l += str(sublevel.info.gateObjectIdealMax)
            else:
                l += '0 - {0}'.format(sublevel.info.gateObjectIdealMax)
            lines.append(l)
        result = appendSortedLines(lines, result)
    
    return result


##
#  Given a cave object, it returns a detailed list of the objects
#  in the specified sublevel index, ready for wiki use.
#  @param cave Cave object.
#  @param sublevelNr Sublevel number, starting at 0.
#  @return The list.
def getDetailedWikiList(cave, sublevelNr):
    sublevel = cave.sublevels[sublevelNr]

    # Calculate main minimums.
    mainMinEntries = []
    for e in sublevel.allEntries:
        if e.category == p2cpc.CAT_MAIN and e.minAmount is not None and e.minAmount > 0:
            mainMinEntries.append(e)
            if e.carrying is not None:
                mainMinEntries.append(sublevel.allEntries[e.carrying - 1])
    
    # Calculate main filler.
    mainFillerEntries = []
    for e in sublevel.allEntries:
        if e.category == p2cpc.CAT_MAIN and e.weight is not None and e.weight > 0:
            mainFillerEntries.append(e)
    nMainFillerSpawns = sublevel.info.mainObjectIdealMax - sublevel.info.mainObjectMinTotal
    
    # Calculate decorative minimums.
    decorativeMinEntries = []
    for e in sublevel.allEntries:
        if e.category == p2cpc.CAT_DECORATIVE and e.minAmount is not None and e.minAmount > 0:
            decorativeMinEntries.append(e)
            if e.carrying is not None:
                decorativeMinEntries.append(sublevel.allEntries[e.carrying - 1])
    
    # Calculate treasure minimums.
    treasureMinEntries = []
    for e in sublevel.allEntries:
        if e.category == p2cpc.CAT_TREASURE and e.carriedBy is None and e.minAmount is not None and e.minAmount > 0:
            treasureMinEntries.append(e)
    
    # Calculate treasure filler.
    treasureFillerEntries = []
    for e in sublevel.allEntries:
        if e.category == p2cpc.CAT_TREASURE and e.weight is not None and e.weight > 0:
            treasureFillerEntries.append(e)
    nTreasureFillerSpawns = sublevel.info.treasureObjectIdealMax - sublevel.info.treasureObjectMinTotal
    
    # Calculate dead end minimums.
    deadEndMinEntries = []
    for e in sublevel.allEntries:
        if e.category == p2cpc.CAT_DEAD_END and e.minAmount is not None and e.minAmount > 0:
            deadEndMinEntries.append(e)
            if e.carrying is not None:
                deadEndMinEntries.append(sublevel.allEntries[e.carrying - 1])
    
    # Calculate dead end filler.
    deadEndFillerEntries = []
    for e in sublevel.allEntries:
        if e.category == p2cpc.CAT_DEAD_END and e.weight is not None and e.weight > 0:
            deadEndFillerEntries.append(e)
            break
    
    # Calculate gate filler.
    gateFillerEntries = []
    for e in sublevel.allEntries:
        if e.category == p2cpc.CAT_GATE and e.weight is not None and e.weight > 0:
            gateFillerEntries.append(e)
            break
    
    # Write header.
    result = '{| class="wikitable mw-collapsible mw-collapsed technicaltable"\n'
    result += '! colspan="5" style="width: 288px;" | {{tt|Detailed object list|This is a representation of the data in the cave\'s file, and how the game makes use of it.}}\n'

    # Write main minimums and carried treasure.
    if len(mainMinEntries) == 0:
        printSublevelError(sublevelNr + 1, 'NO MAIN ENTRIES. UNSUPPORTED SCENARIO. THE DETAILED OBJECT TABLE WILL LOOK WEIRD AND WILL REQUIRE MANUAL TWEAKING.')

    result += writeDetailedMinHeader('The game spawns these "main" objects:')
    for e in mainMinEntries:
        result += writeDetailedMinEntry(e)
    
    # Write main filler.
    if len(mainFillerEntries) > 0 and nMainFillerSpawns > 0:
        
        result += writeDetailedFillerHeader('Alongside it spawns {0} "main" objects. Chances:'.format(nMainFillerSpawns))
        for e in mainFillerEntries:
            result += writeDetailedFillerEntry(e, sublevel.info.mainObjectWeightsSum)
    
    # Write decoration minimums.
    if len(decorativeMinEntries) > 0:

        result += writeDetailedMinHeader('Then it spawns these "decoration" objects:')
        for e in decorativeMinEntries:
            result += writeDetailedMinEntry(e)
    
    # Write treasure minimums.
    if len(treasureMinEntries) > 0:

        result += writeDetailedMinHeader('Then it spawns these "treasure" objects:')
        for e in treasureMinEntries:
            result += writeDetailedMinEntry(e)
    
    # Write treasure filler.
    if len(treasureFillerEntries) > 0 and nTreasureFillerSpawns > 0:

        result += writeDetailedFillerHeader('Then it spawns {0} "treasure" objects. Chances:'.format(nTreasureFillerSpawns))
        for e in sublevel.allEntries:
            result += writeDetailedFillerEntry(e, sublevel.info.treasureObjectWeightsSum)

    # Write dead end minimums.
    if len(deadEndMinEntries) > 0:

        result += writeDetailedMinHeader('Then it spawns these "dead end" objects:')
        for e in deadEndMinEntries:
            result += writeDetailedMinEntry(e)
    
    # Write dead end filler.
    if len(deadEndFillerEntries) > 0:

        result += writeDetailedFillerHeader('Then it spawns "dead end" objects in as many dead ends as it can. Chances:')
        for e in deadEndFillerEntries:
            result += writeDetailedFillerEntry(e, sublevel.info.deadEndObjectWeightsSum)

    # Write gate filler.
    if len(gateFillerEntries) > 0 and sublevel.info.gateObjectIdealMax > 0:

        result += writeDetailedFillerHeader('Then it spawns {0} "gate" objects. Chances:'.format(sublevel.info.gateObjectIdealMax))
        for e in gateFillerEntries:
            result += writeDetailedFillerEntry(e, sublevel.info.gateObjectWeightsSum)
    
    # Write footer.
    result += '|}\n'

    result += ':\'\'For details on how objects are spawned, and how some may fail to spawn, see [[Cave#Generation|here]].\'\'\n'
    
    return result


##
#  Returns the word specified, but with 'a' or 'an' before it, depending on its
#  starting letter.
#  @param s String to process.
#  @return 'a' or 'an' followed by the string.
def aan(s):
    pre = 'a'
    if s[0] == 'a' or s[0] == 'A':
        pre = 'an'
    elif s[0] == 'e' or s[0] == 'E':
        pre = 'an'
    elif s[0] == 'i' or s[0] == 'I':
        pre = 'an'
    elif s[0] == 'o' or s[0] == 'O':
        pre = 'an'
    return '{0} {1}'.format(pre, s)


##
#  Returns the specified subject name, but either in a singular or plural
#  form, depending on the amount specified.
#  @param subject Subject name.
#  @param amount Amount of the subject.
#  @return Subject name, in singular or plural form.
def plural(subject, amount):
    if subject == 'Bulbmin':
        return subject
    if amount == 1 or subject[-1] == 's':
        return subject
    return subject + 's'


##
#  Returns Pikipedia wikitext with the icon and name,
#  plus disambiguation if necessary, of the specified object class.
#  @param objClass Object class to process.
#  @return Pikipedia wikitext with the icon and name.
def getIconAndName(objClass):
    s = '{{{{icon|{0}|y}}}}'.format(constants.OBJECTS[objClass][0])
    if len(constants.OBJECTS[objClass][2]) > 0:
        s += ' ({0})'.format(constants.OBJECTS[objClass][2])
    return s


##
#  Returns Pikipedia wikitext with the minimum and maximum times
#  an object can appear.
#  @param minTimes Minimum number of times.
#  @param maxTimes Maximum number of times, or None.
#  @return Pikipedia wikitext with the times.
def getTimes(minTimes, maxTimes):
    if minTimes == maxTimes:
        return '{0}'.format(minTimes)
    if maxTimes is None:
        if minTimes == 0:
            return 'indefinite amount'
        else:
            return '{0} or more'.format(minTimes)
    return '{0} - {1}'.format(minTimes, maxTimes)


##
#  Given a string, it adds a list of lines after it, but sorts that list first.
#  @param list List of lines to add, without the ending '\n'.
#  @param s String to append the list to.
#  @return The supplied string with the list appended.
def appendSortedLines(list, s):
    list = sorted(list)
    for l in list:
        s += l + '\n'
    return s


##
#  Outputs a processing error in a sublevel.
#  @param sublevelNr Sublevel number in which this occurred. Should start at 1.
#  @param msg Error message to output.
def printSublevelError(sublevelNr, msg):
    print('ERROR IN SUBLEVEL {0}: {1}'.format(sublevelNr, msg))


##
#  Writes down a "minimum amount" section header for the detailed wiki list.
#  @param explanation String explaining what gets spawned in this section.
#  @return String with the info written.
def writeDetailedMinHeader(explanation):
    result = '|-\n'
    result += '! colspan="5" | {0}\n'.format(explanation)
    result += '|-\n'
    result += '! ID !! Object !! Amount !! Fall method !! Spawn location\n'
    return result


##
#  Writes down a "filler" section header for the detailed wiki list.
#  @param explanation String explaining what gets spawned in this section.
#  @return String with the info written.
def writeDetailedFillerHeader(explanation):
    result = '|-\n'
    result += '! colspan="5" | {0}\n'.format(explanation)
    result += '|-\n'
    result += '! ID !! Object !! Chance !! Fall method !! Spawn location\n'
    return result


##
#  Writes down a "minimum amount" entry's info for the detailed wiki list.
#  @param entry The entry to write about.
#  @return String with the info written.
def writeDetailedMinEntry(entry):
    result = ''
    if entry.carriedBy is None:
        result += '|-\n'
        result += '| {0}\n'.format(entry.id)
        result += '| {0}\n'.format(getIconAndName(entry.objClass))
        result += '| {0}\n'.format(entry.minAmount)
        result += '| {0}\n'.format(getFallMethodStr(entry.spawnMethod))
        result += '| {0}\n'.format(getSpawnLocationStr(entry))
    else:
        result += '|-\n'
        result += '| -\n'
        result += '| {0}\n'.format(getIconAndName(entry.objClass))
        result += '| colspan="3" | Carried inside entry with ID {0}\n'.format(entry.carriedBy)
    return result


##
#  Writes down a "filler" entry's info for the detailed wiki list.
#  @param entry The entry to write about.
#  @param weightSums Sum of the weights of entries of this entry's category.
#  @return String with the info written.
def writeDetailedFillerEntry(entry, weightSums):
    result = '|-\n'
    result += '| {0}\n'.format(entry.id)
    if entry.category == p2cpc.CAT_GATE:
        result += '| [[Gate]] ({0:.0f} [[Health|HP]])\n'.format(entry.gateHealth)
    else:
        result += '| {0}\n'.format(getIconAndName(entry.objClass))
    result += '| {0:.0f}%\n'.format(entry.weight / float(weightSums) * 100)
    result += '| {0}\n'.format(getFallMethodStr(entry.spawnMethod))
    result += '| {0}\n'.format(getSpawnLocationStr(entry))
    
    return result


##
#  Returns a string that describes the given fall method.
#  @param method Fall method.
#  @return A string describing the fall method.
def getFallMethodStr(method):
    if method is None:
        return 'None'
    if method == '$1' or method == '$':
        return 'Falls from the sky'
    if method == '$2':
        return 'Falls when Pikmin are nearby'
    if method == '$3':
        return 'Falls when leaders are nearby'
    if method == '$4':
        return 'Falls when Pikmin are carrying nearby'
    if method == '$5':
        return 'Falls if a Purple Pikmin pounds nearby'
    print('UNKNOWN FALL METHOD {0}'.format(method))
    return ''


##
#  Returns a string that describes an object's spawn location, based on
#  numerous factors.
#  @param entry Entry to process.
#  @return A string describing the spawn location.
def getSpawnLocationStr(entry):
    if entry.category == p2cpc.CAT_TREASURE:
        return 'Treasure spots'
    if entry.category == p2cpc.CAT_DEAD_END:
        return 'Dead ends'
    if entry.category == p2cpc.CAT_GATE:
        return 'Gate spots'
    if entry.spawnType == 0:
        return '"Easy" enemy spots'
    if entry.spawnType == 1:
        return '"Hard" enemy spots'
    if entry.spawnType == 2:
        return 'Treasure spots'
    if entry.spawnType == 4:
        return 'Hole/geyser spots'
    if entry.spawnType == 5:
        return 'Cave unit seams'
    if entry.spawnType == 6:
        return 'Plant spots'
    if entry.spawnType == 7:
        return 'Leader spawn spots'
    if entry.spawnType == 8:
        return '"Special" enemy spots'
    print('UNKNOWN SPAWN LOCATION FOR ENTRY OF CATEGORY {0} AND SPAWN TYPE {1}'.format(entry.category, entry.spawnType))
    return ''


##
#  Run the main function.
if __name__ == '__main__':
    main()
