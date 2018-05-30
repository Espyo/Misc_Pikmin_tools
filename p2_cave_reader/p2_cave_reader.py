'''
The purpose of this code is to provide a function, read_cave_from_file(),
that reads a cave file from Pikmin 2, and returns a Cave object filled with information
about the cave. This information is very raw, using internal names, and not separating
the objects by categories.
'''

#TODO Objects in the "decorative" category have the number after the class serve as just the minimum amount
#TODO What is the difference between two Dwarf Red Bulborb entries with min amount 1, and one entry with min amount 2? Surely there must be some


# Data about a cave.
class Cave :
    def __init__(self) :
        self.sublevels = []

# Data about a cave's sublevel.
class Sublevel :
    def __init__(self) :
        self.info = SublevelInfo()
        self.teki_objects = []
        self.item_objects = []
        self.gate_objects = []
        self.cap_objects = []

# Data about a sublevel's parameters.
class SublevelInfo :
    def __init__(self) :
        # Slightly unknown {f000} parameter. Seems to always reflect the sublevel number.
        self.sublevel_number_f000 = None
        # Same as {f000} but it's {f001}.
        self.sublevel_number_f001 = None
        # Ideal max number of objects for objects in the "main" category.
        self.main_object_ideal_max = None
        # Ideal max number of objects for objects in the "treasure" category.
        self.treasure_object_ideal_max = None
        # Ideal max number of gates.
        self.gate_object_ideal_max = None
        # Number of room cave units.
        self.room_units = None
        # Ratio between how many corridors and room units there are.
        self.corridor_room_ratio = None
        # Does the sublevel have an exit geyser?
        self.has_geyser = None
        # Name of the file that lists the cave units to use.
        self.cave_unit_list_filename = ""
        # Name of the file that declares the lighting to use.
        self.lighting_filename = ""
        # Name of the skybox to use.
        self.skybox = ""
        # Is the next sublevel hole clogged?
        self.has_clog = None
        # Unknown.
        self.unknown_f011 = None
        # Music type. 0 is normal, 1 is boss, 2 is rest.
        self.music_type = None
        # Does the sublevel have an invisible floor plain, or do objects fall into the abyss?
        self.has_floor = None
        # Maximum number of dead end cave units.
        self.dead_end_max = None
        # If 0, all CapInfo objects are ignored.
        self.has_dead_end_objects = None
        # Time until the Waterwraith appears.
        self.waterwraith_time = None
        # Unused. If 1, seesaw blocks show up randomly.
        self.has_seesaw_blocks = None

# Data about an object entry in a sublevel.
class Object :
    def __init__(self) :
        # Just the object's class. This uses whatever capitalization is in the file.
        self.obj_class = ""
        # Class of the object this enemy is carrying, if any. Again, the capitalization is unchanged.
        self.carrying = None
        # Spawn method. None if none is specified, otherwise it's a string with the "$" and the (optional) number.
        self.spawn_method = None
        # Minimum amount of this entry to spawn.
        self.min_amount = None
        # Random distribution weight.
        self.weight = None
        # Type of spawn point to use.
        self.spawn_type = None
        # Type of dead end unit to use, for entries in CapInfo.
        self.cap_type = None

# Data about a gate entry.
class Gate :
    def __init__(self) :
        # Word used to describe this gate. It's always "gate".
        self.keyword = ""
        # This gate's health.
        self.health = None
        # Random distribution weight.
        self.weight = None


# Reads a cave file and returns a Cave object filled with the cave's data.
def read_cave_from_file(infile) :
    cave_data = Cave()
    
    read_caveinfo(infile, cave_data)
    
    for s in range(len(cave_data.sublevels)) :
        read_floorinfo(infile, cave_data, s)
        read_tekiinfo(infile, cave_data, s)
        read_iteminfo(infile, cave_data, s)
        read_gateinfo(infile, cave_data, s)
        read_capinfo(infile, cave_data, s)
    
    return cave_data


# Reads the CaveInfo block in a text file and fills the cave data object.
def read_caveinfo(infile, cave_data) :
    searching_start = True
    
    for line in infile :
        line = clean_line(line)
        if len(line) == 0 : continue
        
        if searching_start :
            if line == '{':
                searching_start = False
        
        else :
            if line.find("{c000}") != -1 :
                sublevel_total = int(line[9:])
                for s in range(sublevel_total) :
                    cave_data.sublevels.append(Sublevel())
                
            elif line.find("{_eof}") != -1 :
                return


# Reads the FloorInfo block in a text file and fills the cave data object.
def read_floorinfo(infile, cave_data, sublevel_nr) :
    searching_start = True
    
    for line in infile :
        line = clean_line(line)
        if len(line) == 0 : continue
        
        if searching_start :
            if line == '{':
                searching_start = False
        
        else :
            info = cave_data.sublevels[sublevel_nr].info
            words = line.split()
            
            if words[0] == "{f000}" :
                info.sublevel_number_f000 = int(words[2])
            elif words[0] == "{f001}" :
                info.sublevel_number_f001 = int(words[2])
            elif words[0] == "{f002}" :
                info.main_object_ideal_max = int(words[2])
            elif words[0] == "{f003}" :
                info.treasure_object_ideal_max = int(words[2])
            elif words[0] == "{f004}" :
                info.gate_object_ideal_max = int(words[2])
            elif words[0] == "{f005}" :
                info.room_units = int(words[2])
            elif words[0] == "{f006}" :
                info.corridor_room_ratio = float(words[2])
            elif words[0] == "{f007}" :
                info.has_geyser = int(words[2])
            elif words[0] == "{f008}" :
                info.cave_unit_list_filename = words[2]
            elif words[0] == "{f009}" :
                info.lighting_filename = words[2]
            elif words[0] == "{f00A}" :
                info.skybox = words[2]
            elif words[0] == "{f010}" :
                info.has_clog = int(words[2])
            elif words[0] == "{f011}" :
                info.unknown_f011 = words[2]
            elif words[0] == "{f012}" :
                info.music_type = int(words[2])
            elif words[0] == "{f013}" :
                info.has_floor = int(words[2])
            elif words[0] == "{f014}" :
                info.dead_end_max = int(words[2])
            elif words[0] == "{f015}" :
                info.has_dead_end_objects = int(words[2])
            elif words[0] == "{f016}" :
                info.waterwraith_time = float(words[2])
            elif words[0] == "{f017}" :
                info.has_seesaw_blocks = int(words[2])
            elif words[0] == "{_eof}" :
                return


# Reads the TekiInfo block in a text file and fills the cave data object.
def read_tekiinfo(infile, cave_data, sublevel_nr) :
    searching_start = True
    searching_count = True
    next_is_weight = True
    entry_count = 0
    entry_nr = 0
    
    for line in infile :
        line = clean_line(line)
        if len(line) == 0 : continue
        
        if searching_start :
            if line == '{':
                searching_start = False
        
        elif searching_count :
            entry_count = int(line)
            if entry_count == 0 : return
            for e in range(entry_count) :
                cave_data.sublevels[sublevel_nr].teki_objects.append(Object())
            searching_count = False
        
        else :
            obj = cave_data.sublevels[sublevel_nr].teki_objects[entry_nr]
            if next_is_weight :
                words = line.split()
                
                if words[0][0] == '$' :
                    if words[0][1].isdigit() :
                        obj.spawn_method = words[0][0:1]
                        words[0] = words[0][2:]
                    else :
                        obj.spawn_method = '$'
                        words[0] = words[0][1:]
                
                underscore_pos = words[0].find("_")
                if(underscore_pos != -1) :
                    obj.obj_class = words[0][:underscore_pos]
                    obj.carrying = words[0][underscore_pos + 1:]
                else :
                    obj.obj_class = words[0]
                
                obj.weight = int(words[1][-1])
                s = words[1][:-1]
                if len(s) == 0 :
                    s = "0"
                obj.min_amount = int(s)
                
                next_is_weight = False
                
            else :
                obj.spawn_type = int(line)
                
                next_is_weight = True
                entry_nr += 1
            
            if entry_nr == entry_count :
                return
            
    
# Reads the ItemInfo block in a text file and fills the cave data object.
def read_iteminfo(infile, cave_data, sublevel_nr) :
    searching_start = True
    searching_count = True
    entry_count = 0
    entry_nr = 0
    
    for line in infile :
        line = clean_line(line)
        if len(line) == 0 : continue
        
        if searching_start :
            if line == '{':
                searching_start = False
        
        elif searching_count :
            entry_count = int(line)
            if entry_count == 0 : return
            for e in range(entry_count) :
                cave_data.sublevels[sublevel_nr].item_objects.append(Object())
            searching_count = False
        
        else :
            obj = cave_data.sublevels[sublevel_nr].item_objects[entry_nr]
            words = line.split()
            
            obj.obj_class = words[0]
            obj.weight = int(words[1][-1])
            s = words[1][:-1]
            if len(s) == 0 :
                s = "0"
            obj.min_amount = int(s)
            
            entry_nr += 1
            
            if entry_nr == entry_count :
                return


# Reads the GateInfo block in a text file and fills the cave data object.
def read_gateinfo(infile, cave_data, sublevel_nr) :
    searching_start = True
    searching_count = True
    next_is_health = True
    entry_count = 0
    entry_nr = 0
    
    for line in infile :
        line = clean_line(line)
        if len(line) == 0 : continue
        
        if searching_start :
            if line == '{':
                searching_start = False
        
        elif searching_count :
            entry_count = int(line)
            if entry_count == 0 : return
            for e in range(entry_count) :
                cave_data.sublevels[sublevel_nr].gate_objects.append(Gate())
            searching_count = False
        
        else :
            obj = cave_data.sublevels[sublevel_nr].gate_objects[entry_nr]
            if next_is_health :
                words = line.split()
                
                obj.keyword = words[0]
                obj.health = float(words[1])
                
                next_is_health = False
                
            else :
                obj.weight = int(words[1][-1])
                
                next_is_health = True
                entry_nr += 1
            
            if entry_nr == entry_count :
                return


# Reads the CapInfo block in a text file and fills the cave data object.
def read_capinfo(infile, cave_data, sublevel_nr) :
    searching_start = True
    searching_count = True
    next_is_cap_type = True
    next_is_weight = False
    entry_count = 0
    entry_nr = 0
    
    for line in infile :
        line = clean_line(line)
        if len(line) == 0 : continue
        
        if searching_start :
            if line == '{':
                searching_start = False
        
        elif searching_count :
            entry_count = int(line)
            if entry_count == 0 : return
            for e in range(entry_count) :
                cave_data.sublevels[sublevel_nr].cap_objects.append(Object())
            searching_count = False
        
        else :
            obj = cave_data.sublevels[sublevel_nr].cap_objects[entry_nr]
            if next_is_cap_type :
                obj.cap_type = int(line)
                
                next_is_cap_type = False
                next_is_weight = True
                
            elif next_is_weight :
                words = line.split()
                
                if words[0][0] == '$' :
                    obj.spawn_method = int(words[0][1])
                    words[0] = words[0][2:]
                underscore_pos = words[0].find("_")
                if(underscore_pos != -1) :
                    obj.obj_class = words[0][:underscore_pos]
                    obj.carrying = words[0][underscore_pos + 1:]
                else :
                    obj.obj_class = words[0]
                obj.weight = int(words[1][-1])
                s = words[1][:-1]
                if len(s) == 0 :
                    s = "0"
                obj.min_amount = int(s)
                
                next_is_cap_type = False
                next_is_weight = False
                
            else :
                obj.spawn_type = int(line)
                
                next_is_cap_type = True
                next_is_weight = False
                entry_nr += 1
            
            if entry_nr == entry_count :
                return

# Cleans a line, removing its comments and indentation.
def clean_line(line) :
    number_sign_pos = line.find("#")
    
    if number_sign_pos != -1 :
        line = line[0:number_sign_pos]
    
    line = line.strip(" \t\r\n")
    
    return line
