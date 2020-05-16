import sys, csv, argparse, string, CppHeaderParser

parser = argparse.ArgumentParser("")
parser.add_argument("input", help="the input csv file")
parser.add_argument("--output", default="rom.SYM", help="the output file")
parser.add_argument("--header", default="", help="optional path to an .h file to generate labelling for custom data types")
parser.add_argument("--nostrip", default=False, help="dont remove auto-generated labels")
parser.add_argument("--append", default=False, help="append to existing file")
args = parser.parse_args()

INPUT = args.input
NOSTRIP = args.nostrip
OUTPUT = args.output
APPEND = args.append
HEADER = args.header

ASCII = {"char"}
BYTE = {"byte", "undefined", "undefined1"}
HWORD = {"ushort", "short", "undefined2"}
WORD = {"uint", "int", "undefined4", "pointer", "unsigned int"}
OTHER = {"void", "", "Data Type"}
file = open(INPUT)
csv = csv.reader(file)
sym = open(OUTPUT, "a" if APPEND else "w+")

# Load header file
if HEADER:
    try:
        cppHeader = CppHeaderParser.CppHeader(HEADER)
    except CppHeaderParser.CppParseError as e:
        print(e)
        sys.exit(1)



        
def convert_and_pad(data, bytesize):
        _f = data.split('[')[1].split(']')[0]
        _f = format(int(_f) * bytesize, 'x')
        _f = _f.zfill(4)
        return _f

    #".byt:" + '{0:03d}'.format(format(int(data.split('[')[1].split(']')[0]), 'x')))

def write_base_unit(_addr, _data):
    if _data in ASCII:
        sym.write(_addr + " " + ".asc:0001" + "\n")
        return
        
    elif _data in BYTE:
        sym.write(_addr + " " + ".byt:0001" + "\n")
        return
        
    elif _data in HWORD:
        sym.write(_addr + " " + ".wrd:0002" + "\n")
        return
        
    elif _data.endswith('*') or _data in WORD:
        sym.write(_addr + " " + ".dbl:0004" + "\n")
        return
def is_array(_data):
    if "char[" in _data:
        return ASCII
    elif any(s+"[" in _data for s in BYTE):
        return BYTE
    elif any(s+"[" in _data for s in HWORD):
        return HWORD
    elif any(s+"[" in _data for s in WORD) or "* [" in _data:
        return HWORD
    else:
        return
    
def write_base_unit_array(_addr, _data):
    _t = is_array(_data)
    if not _t:
        return
    elif _t is ASCII:
        sym.write(_addr + " " + ".asc:" + convert_and_pad(_data, 1) + "\n")

    elif _t is BYTE:
        sym.write(_addr + " " + ".byt:" + convert_and_pad(_data, 1) + "\n")

    elif _t is HWORD:
        sym.write(_addr + " " + ".wrd:" + convert_and_pad(_data, 2) + "\n")
        
    elif _t is WORD:
        sym.write(_addr + " " + ".dbl:" + convert_and_pad(_data, 4) + "\n")
        
    return

def csv_convert():
    
    for row in csv:


        addr = row[1]
        name = row[0]
        data = row[3]

        if HEADER:
            header_convert(addr, name, data)
        
        if name == "Name": # beginning of csv
            continue

        # removes entries for external adresses and other invalids
        try:
            a = int(addr, 16)
        except ValueError:
            print ("Did not resolve address for " + name)
            continue

        # remove auto-generated labels, not sure if HIGH interrupts are ever used on gba but idc 
        if not NOSTRIP:
            if name[:4] == "FUN_" and all(c in string.hexdigits for c in name[4:]):
                #print("Stripped " + name)
                continue

            elif name[:6] == "caseD_" and all(c in string.hexdigits for c in name[6:]):
                #print("Stripped " + name)
                continue

            elif name[:12] == "switchdataD_" and all(c in string.hexdigits for c in name[12:]):
                #print("Stripped " + name)
                continue

            elif name == "switchD":
                #print("Stripped " + name)
                continue
            # maybe resolve address tables in the future?
            elif name[:9] == "AddrTable" and all(c in string.hexdigits for c in name[9:]):
                #print("Stripped " + name)
                continue

            elif name[:10] == "thunk_FUN_" and all(c in string.hexdigits for c in name[10:]):
                #print("Stripped " + name)
                continue
            
            elif name[:14] == "thunk_EXT_FUN_" and all(c in string.hexdigits for c in name[14:]):
                #print("Stripped " + name)
                continue

        sym.write(addr + " " + name + "\n")
        
        #convert arrays
        if any(ch in data for ch in {'[', ']'}):
            write_base_unit_array(addr, data)
            continue

        #convert lone units
        write_base_unit(addr, data)

def resolve(_data, _addr, offset, name):
    if _data in cppHeader.classes:

        sym.write(hex(int(_addr, 16) + offset)[2:].zfill(8) + " " + name + "\n")
        
        #c (class) can be a struct or enum
        c = cppHeader.classes[_data]["properties"]["public"]

        #go over every property, if it's not a base unit then resolve it further
        for p in c:

            # only will write lone base units
            write_base_unit(hex(int(_addr, 16) + offset)[2:].zfill(8), p["type"])
            sym.write(hex(int(_addr, 16) + offset)[2:].zfill(8) + " " + name + "->" + p["name"] + "\n")

            if p["type"] in ASCII:
                offset = offset + 0x1
            elif p["type"] in BYTE:
                offset = offset + 0x1
            elif p["type"] in HWORD:
                offset = offset + 0x2
            elif p["type"] in WORD or p["type"].endswith("*"):
                offset = offset + 0x4
                
            elif _t := is_array(p["type"]):

                #this will write array if it is a base unit
                write_base_unit_array(hex(int(_addr, 16) + offset)[2:].zfill(8), p["name"])

                # use convert_and_pad here to find the array len
                if _t is BYTE or _t is ASCII:
                    offset = offset + convert_and_pad(p["type"], 1)
                if _t is HWORD:
                    offset = offset + convert_and_pad(p["type"], 2)
                if _t is WORD:
                    offset = offset + convert_and_pad(p["type"], 4)
                
            else:
                print("resolving", _data, "->", p["type"], "current offset", offset)

                # data (struct) -> p (another struct)
                # example linkObj->inventory
                # that way we can have linkObj->inventory->bow as our label
                # instead of inentory->bow
                resolve(p["type"], _addr, offset, _data + "->" + p["type"])
                #print(cppHeader.classes[data]["properties"]["public"])
                #offset = offset + int(input("write the number of bytes this data type occupies: \n"))
        return offset
    
def header_convert(addr, name, data):
    # Read the labels to see where and if the user defined data types are actually implemented
    # for each base unit contained within each user data type, we need to perform the same process as before
    # create a label as well as define its base unit type


    # if it is a ptr or array of ptrs, it still behaves like a WORD
    if any(s in data for s in (" *", "* [")):
        return

    # filter out base units
    if data in ASCII or data in BYTE or data in HWORD or data in WORD or data in OTHER:
        return

    # resolve is ran recursively, the third address is used internally to keep track of
    # our location within the user defined data type
    resolve(data, addr, 0x0, name)
        
        #print(data)
        
                #write_base_unit()
                #print(p)
                #print(data + "->" + p["name"])

    #for c in cppHeader.classes:
        #struct name
        #print(cppHeader.classes[c]["properties"])
        #print("\n\n\n")
        #for d in c:
            #print(type(d))

       

csv_convert()

file.close()
sym.close()

