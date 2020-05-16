import csv, argparse, string

parser = argparse.ArgumentParser("")
parser.add_argument("input", help="the input csv file")
parser.add_argument("--output", default="rom.SYM", help="the output path")
parser.add_argument("--nostrip", default=False, help="dont remove auto-generated labels")
parser.add_argument("--append", default=False, help="append to existing file")
args = parser.parse_args()

INPUT = args.input
NOSTRIP = args.nostrip
OUTPUT = args.output
APPEND = args.append

ASCII = {"char", "string"}
BYTE = {"byte", "undefined"}
HWORD = {"ushort", "short", "undefined2"}
WORD = {"uint", "int", "undefined4"}

file = open(INPUT)
csv = csv.reader(file)
sym = open(OUTPUT, "a" if APPEND else "w+")


for row in csv:

    addr = row[1]
    name = row[0]
    data = row[3]

    # removes entries for external adresses and other invalids
    try:
        a = int(addr, 16)
    except ValueError:
        print ("Could not resolve address for " + name)
        continue

    # remove auto-generated labels, not sure if HIGH interrupts are ever used on gba but idc 
    if not NOSTRIP:
        if name[:4] == "FUN_" and all(c in string.hexdigits for c in name[4:]):
            print("Stripped " + name)
            continue

        if name[:6] == "caseD_" and all(c in string.hexdigits for c in name[6:]):
            print("Stripped " + name)
            continue

        if name[:12] == "switchdataD_" and all(c in string.hexdigits for c in name[12:]):
            print("Stripped " + name)
            continue

        if name == "switchD":
            print("Stripped " + name)
            continue

        if name[:9] == "AddrTable" and all(c in string.hexdigits for c in name[9:]):
            print("Stripped " + name)
            continue

        if name[:10] == "thunk_FUN_" and all(c in string.hexdigits for c in name[10:]):
            print("Stripped " + name)
            continue

        if name[:14] == "thunk_EXT_FUN_" and all(c in string.hexdigits for c in name[14:]):
            print("Stripped " + name)
            continue

    sym.write(addr + " " + name + "\n")
    
    if data in ASCII:
        sym.write(addr + " " + ".asc:0001" + "\n")
        
    if data in BYTE:
        sym.write(addr + " " + ".byt:0001" + "\n")
        
    if data in HWORD:
        sym.write(addr + " " + ".wrd:0002" + "\n")
        
    if data.endswith('*') or data in WORD:
        sym.write(addr + " " + ".dbl:0004" + "\n")

file.close()
sym.close()
