#TODO test the checksum
#TODO all of the unknown fields

import io
import json
import struct
import sys
from zlib import crc32
from file_map import file_map

fm = file_map.FileMap()

'''
========================
Main function.
'''
def main() :
    if len(sys.argv) < 2 :
        print("Hey! Pikmin save editor, by Espyo, with help from Yoshi2")
        print("Usage: " + sys.argv[0] + " <input file> [<output file>]")
        print("")
        print("This tool can convert a Hey! Pikmin save file from, and to, a plain JSON text file that can be edited.")
        print("What it does is determined automatically by the input file's extension.")
        print("")
        print("Notes:")
        print("* This was made with Citra save files in mind ('radish*.sav').")
        print("* When creating a SAV file, the checksum is adjusted automatically.")
        print("* More info: http://pikmintkb.shoutwiki.com/wiki/Hey!_Pikmin_save_file")
        return -1
    
    input_fn = sys.argv[1]
    output_fn = ""
    sav_to_json = False
    
    split_fn = input_fn.split(".")
    if len(split_fn) > 1 and split_fn[1] == "sav" :
        sav_to_json = True
        output_fn = split_fn[0] + ".json"
    else :
        output_fn = split_fn[0] + ".sav"
        
    if len(sys.argv) >= 3 :
        output_fn = sys.argv[2]
    
    file_map.init_file_map(fm)
    
    if sav_to_json :
        do_sav_to_json(input_fn, output_fn)
    else :
        do_json_to_sav(input_fn, output_fn)


'''
========================
Convert from SAV to JSON.
'''
def do_sav_to_json(input_fn, output_fn) :
    input = open(input_fn, "rb")
    output = io.open(output_fn, "w", encoding="utf-8")
    raw = input.read()
    
    blocks = {}
    i = 0
    for b in fm.blocks :
        block = {}
        blocks[b.name] = block
        magic = raw[i : i + 4].decode("ascii")
        i = i + 4
        if magic != b.magic :
            raise RuntimeError("In byte " + hex(i) + ", expected block header \"" + b.magic + "\", found \"" + str(magic) + "\".")
        for d in b.data :
            if d.type == file_map.DATA_UINT8 :
                block[d.name] = ba_to_uint8(raw, i)
                i = i + 1
            elif d.type == file_map.DATA_UINT16 :
                block[d.name] = ba_to_uint16(raw, i)
                i = i + 2
            elif d.type == file_map.DATA_UINT32 :
                block[d.name] = ba_to_uint32(raw, i)
                i = i + 4
        
    json.dump(blocks, output, indent = 4, separators = (",", ": "), sort_keys = True)
    print("Dump to " + output_fn + " successful.")


'''
========================
Convert from JSON to SAV.
'''
def do_json_to_sav(input_fn, output_fn) :
    input = open(input_fn, "r", encoding="utf-8")
    output = io.open(output_fn, "wb")
    blocks = json.load(input)
    
    raw = []
    i = 0
    for b in fm.blocks :
        if b.name not in blocks :
            raise RuntimeError("Could not find block \"" + b.name + "\" in the JSON data.")
        
        raw.append(b.magic.encode("ascii")[0])
        raw.append(b.magic.encode("ascii")[1])
        raw.append(b.magic.encode("ascii")[2])
        raw.append(b.magic.encode("ascii")[3])
        i = i + 4
        for d in b.data :
            if d.name not in blocks[b.name] :
                raise RuntimeError("Could not find data \"" + d.name + "\" in block \"" + b.name + "\" in the JSON data.")
            
            if d.type == file_map.DATA_UINT8 :
                uint8_to_ba(raw, blocks[b.name][d.name])
                i = i + 1
            elif d.type == file_map.DATA_UINT16 :
                uint16_to_ba(raw, blocks[b.name][d.name])
                i = i + 2
            elif d.type == file_map.DATA_UINT32 :
                uint32_to_ba(raw, blocks[b.name][d.name])
                i = i + 4
    
    # Update the checksum.
    new_chk = crc32(bytearray(raw[file_map.CHECKSUM_LOCATION + 4 : -1]))
    raw[file_map.CHECKSUM_LOCATION + 0] = struct.pack("I", new_chk)[0]
    raw[file_map.CHECKSUM_LOCATION + 1] = struct.pack("I", new_chk)[1]
    raw[file_map.CHECKSUM_LOCATION + 2] = struct.pack("I", new_chk)[2]
    raw[file_map.CHECKSUM_LOCATION + 3] = struct.pack("I", new_chk)[3]
    
    output.write(bytearray(raw))
    output.close()
    print("Saved " + output_fn + " successfully.")


'''
========================
Utils.
'''
def ba_to_uint8(a, i) :
    return struct.unpack("B", a[i : i + 1])[0]
def ba_to_uint16(a, i) :
    return struct.unpack("<H", a[i : i + 2])[0]
def ba_to_uint32(a, i) :
    return struct.unpack("<I", a[i : i + 4])[0]

def uint8_to_ba(a, v) :
    a.append(struct.pack("B", v)[0])
def uint16_to_ba(a, v) :
    a.append(struct.pack("<H", v)[0])
    a.append(struct.pack("<H", v)[1])
def uint32_to_ba(a, v) :
    a.append(struct.pack("<I", v)[0])
    a.append(struct.pack("<I", v)[1])
    a.append(struct.pack("<I", v)[2])
    a.append(struct.pack("<I", v)[3])

def read_uint32(f) :
    return struct.unpack(">I", f.read(4))[0]
def read_uint16(f) :
    return struct.unpack(">H", f.read(2))[0]
def read_uint8(f) :
    return struct.unpack("B", f.read(1))[0]
def read_uint24(f) :
    upperval = read_uint8(f)
    lowerval = read_uint16(f)
    return (upperval << 16) | lowerval


'''
========================
'''
if __name__=="__main__":
    main()
