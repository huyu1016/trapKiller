import os
print(os.getcwd())
print(os.path.isfile("./sol/TS.sol"))
with open('./opcodes/example.opcodes', 'r') as f:
    line = f.readline()
    print(line)