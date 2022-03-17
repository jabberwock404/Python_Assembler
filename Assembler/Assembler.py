# Author: JW

import sys

#global variables
compInstrct = {"AND": "0xxx", "ADD": "1xxx", "LDA": "2xxx", "STA": "3xxx",
               "BUN": "4xxx", "BSA": "5xxx", "ISZ": "6xxx",
               "CLA": "7800", "CLE": "7400", "CMA": "7200", "CME": "7100",
               "CIR": "7080", "CIL": "7040", "INC": "7020", "SPA": "7010",
               "SNA": "7008", "SZA": "7004", "SZE": "7002", "HLT": "7001",
               "INP": "F800", "OUT": "F400", "SKI": "F200", "SKO": "F100",
               "ION": "F080", "IOF": "F040"}

IcompInstrct = {"AND": "8xxx", "ADD": "9xxx", "LDA": "Axxx", "STA": "Bxxx",
                "BUN": "Cxxx", "BSA": "Dxxx", "ISZ": "Exxx"}

variables = {}

original_stdout = sys.stdout

# functions
def tohex(val):
  return hex((val + (1 << 16)) % (1 << 16))

def replace_line(file_name, line_num, i):
    lines = open(file_name, 'r').readlines()
    for x, y in zip(IcompInstrct, compInstrct):
        if IcompInstrct[x] in lines[line_num] or compInstrct[y] in lines[line_num]:
            lines[line_num] = lines[line_num].replace("xxx", variables[i])
            break
    out = open(file_name, 'w')
    out.writelines(lines)
    out.close()

def clean(file_name, curr):
    lines = open(file_name, 'r').readlines()
    lines[curr] = ""
    out = open(file_name, 'w')
    out.writelines(lines)
    out.close()

def printVariables(file):
    newFile = file.strip('.asm')
    sym = newFile + "Sym.txt"
    with open(sym, "w") as write:
        for i in variables:
            print(i + " " + variables[i])
            write.write(i + " " + variables[i] + "\n")

def parser(file):
    contents = ""
    address = hex(0)
    newFile = file.strip('.asm')
    txt = newFile + "Bin.txt"
    with open(file, "r") as program:
        with open(txt, "w") as f:
            #loop through assembly
            for line in program:
                toPrint = False

                # get starting addresses
                if line == "ORG 200":
                    print("")
                if "ORG" in line:
                    for s in line.split():
                        if s.isdigit():
                            s = "0x" + s
                            address = hex(int(s, 16))
                else:
                    toPrint = True

                #get indirect instruction
                if "I" in line:
                    for s in line.split():
                        if "I" == s:
                            for i in IcompInstrct:
                                if i in line:
                                    contents = IcompInstrct[i]
                        else:
                            for j in compInstrct:
                                if j in s:
                                    contents = compInstrct[j]

                #get standard computer instruction
                else:
                    for j in compInstrct:
                        if j in line:
                            contents = compInstrct[j]

                #get address of variable and place in hash table
                if "," in line:
                    variables[line[0:3]] = str(address)[2:]

                #find variables
                if "HEX" in line:
                    for s in line.split():
                        if s.isdigit():
                            contents = s
                            break
                        elif "," in s or "HEX" in s:
                            contents = ""
                        else:
                            contents = s
                            break

                elif "DEC" in line:
                    for s in line.split():
                        if s.isdigit():
                            if int(s) == 0:
                                contents = "0000"
                                break
                            else:
                                contents = str(hex(int(s))).strip("0x")
                                break
                        elif s.startswith("-"):

                            #figure out proper conversion
                            contents = str(tohex(int(s))).strip("0x")
                            break

                #send to file
                if toPrint == True:
                    f.write(str(address) + ": " + contents + "\n")
                    address = hex(int(address, 16) + 1)
                    contents = ""
    program.close()
    f.close()

    #insert variable address into program contents
    with open(file, "r") as program, open(txt, "r+") as f:
        curr = 0

        #loop through assembly
        for lineA in program:
            used = False
            for i in variables:
                if i in lineA:

                    #double check variable assignment
                    if i + "," in lineA:
                        for j in lineA.split():
                            if i == j:
                                replace_line(txt, curr, i)
                                curr = curr + 1
                                used = True
                                break
                    else:
                        replace_line(txt, curr, i)
                        curr = curr + 1
                        used = True
                        break

            #increment line number in bin file
            if "ORG" in lineA:
                print()
            elif "          " in lineA or len(lineA) and used == False:
                curr = curr + 1

    program.close()
    f.close()

    print("##########################################################\n")

    #clean file
    print("Instructions:")
    with open(txt, "r") as f:
        curr = 0
        for lin in f:
            if len(lin) == 8:
                clean(txt, curr)
            else:
                print(lin.strip("\n"))
                curr = curr + 1

#def
# main()
print("##########################################################\n")
print("Welcome to the my Assembler!\n")
print("##########################################################")
proceed = True
while proceed:

    fileInp = input("Type the file you want to assemble (make sure it is in the same directory as this program): ")
    parser(fileInp)
    print("\n")

    print("##########################################################")

    answer = input("Would you like to view the Symbols Table? (and generate Symbol File?) (y/n): ")
    if answer == "y" or answer == "yes":
        printVariables(fileInp)

    print("##########################################################")

    answer = input("Would you like to run again? (y/n): ")
    if answer == "n" or answer == "no":
        proceed = False
    else:
        proceed = True