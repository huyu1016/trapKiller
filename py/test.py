# from solcx import install_solc
import re
import os

# rootDir = "./dataset/"
# a= "======0x0267ee183beebdb7f931afe41e4e25352195b871,BulleonCrowdsale=======N"
# b = a.split('======')
# print(b)
# mainContent = b[1]

# mainRes = mainContent.split(',')
# fileName = mainRes[0]
# mainContractName = mainRes[1]
# print(fileName,mainContractName)

# with open("./bin-full/BLTTokenSale.bin",'r') as f:
#     str=f.read()
#     print(len(str))
#     print(hex(len(str)))
# solFilePath = "./git-dataset/"

# list_dirs = os.walk(solFilePath)
# for _,_,files in list_dirs:
#     for f in files:
#         str_list = f.split('_')
#         address = str_list[0]
#         last_str = str_list[1].strip()
#         mainName = last_str.split('.')[0].strip()
#         print(mainName)

# install_solc("0.8.0")

# match_string = "pragma so2lidity3123"
# pattern = re.compile(r'pragma solidity')
# if re.search(pattern, match_string):
#     print("Found match!")
# else:
#     print("No match found.")
# solFilePath = "./git-dataset/Ff385787bcC68D2158015a3bc22504b72Be485bA_VeeBits.sol"
# with open(solFilePath, 'r',encoding='utf-8') as disasm_file:
#     while True:
#         line = disasm_file.readline()
#         if not line:
#             break
#         pattern = re.compile(r'pragma solidity')
#         if re.search(pattern, line):
#             detail_pattern = r"\^?(\d+\.\d+\.\d+)"
#             match = re.search(detail_pattern, line)
#             if match:
#                 version = match.group(1)
#                 print(version)
#             break
#         else:
#             continue
# solcVersionPath = "C:\\Users\\yafei\\.solcx"
# list_dirs = os.walk(solcVersionPath)
# for _,dirs,files in list_dirs:
#     for dir in dirs:
#          version_list = dir.split('v')
#          print(version_list[1].strip())


# if os.path.isfile("./output.xlsx"):
#     os.remove("./output.xlsx")
# with open("./bin-full/FlatPricingExt.bin",'r') as f:
#     str = f.read()
#     res = re.search(r'(\_\_\.).*(\_\_)',str)
#     if res:
#         res_final = str[:res.start()] + str[res.end():]
#         f.close()
#         with open("./bin-full/FlatPricingExt.bin",'w') as w:
#             w.write(res_final)
            # w.close()

# str = "123123__.\dataset\0x07cede39f98e7ba4b8fe0728__123asdfasdasd__.\dataset\0x07cede39f98e7ba4b8fe0728__1312"
# res = re.search(r'(\_\_\.).*(\_\_)',str)
# if res:
#     print(res)
#     print(res.start())
#     print(res.end())
#     res_final = str[:res.start()] + str[res.end():]
#     print(res_final)
path = "./git-dataset/ffCDAbF3DF5E4d5177B578eDE40Ff6284AdB4306_PolysRoyaltiesSplitter.sol"
with open(path,'r',encoding='utf-8') as disasm_file:
        while True:
            line = disasm_file.readline().strip()
            if not line:
                break
            pattern = re.compile(r'pragma solidity')
            if re.search(pattern, line):
                detail_pattern = r"\^?(\d+\.\d+\.\d+)"
                match = re.search(detail_pattern, line)
                if match:
                    print(match.group(1).strip())
                break
            else:
                continue
a = []
a.c
# with open("./bin-full/BLTTokenSale.bin",'r',encoding='utf-8') as f:
#     str_full = f.read()
#     f.close()
# with open("./bin-runtime/BLTTokenSale.bin-runtime",'r',encoding='utf-8') as f:   
#     str_run = f.read()
#     f.close()
# bin_creation = str_full[:len(str_full)-len(str_run)]
# with open("./bin-creation/BLTTokenSale.bin-creation",'w',encoding='utf-8') as f:   
#     f.write(bin_creation)
#     f.close()

# with open("./labeled.txt", encoding='utf-8') as f:
#     contents = f.readlines()
#     print(contents.__len__())