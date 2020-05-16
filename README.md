# ghidra_gba
Convert data types and labels from Ghidra into a .SYM file

## csv_to_sym.py
Converts labels exported from Ghidra in csv format to a .SYM file. Useful for debugging in No$Gba.

Optionally (but highly recommended) you can also export labels from a header file containing user defined data types.

![Screenshot](https://i.ibb.co/z84rQcy/Capture.png)

## Installation
Requires CppHeaderParser and ply.

`py -m pip -r requirements.txt`

## Usage
`py csv_to_sym.py csv_file.csv --output rom.SYM --header header_file.h`


You can export labels from Ghidra by selecting labels in the Symbol Table window -> Right Click -> Convert to CSV

You can export a header file from Ghidra in the Data Type Manager window -> Right Click on your rom's category -> Export C Header

Take a look at example_csv.csv and example_header.h if you are unsure if you exported the right format.

Your .SYM file must have the same name as the loaded rom and must be in the same directory if you want to use it with No$Gba.


## Todo
Bitfields do not import properly

Probably other bugs
