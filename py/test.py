import re
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

with open("./bin-full/FlatPricingExt.bin",'r') as f:
    str = f.read()
    res = re.search(r'(\_\_\.).*(\_\_)',str)
    if res:
        res_final = str[:res.start()] + str[res.end():]
        f.close()
        with open("./bin-full/FlatPricingExt.bin",'w') as w:
            w.write(res_final)
            w.close()

# str = "123123__.\dataset\0x07cede39f98e7ba4b8fe0728__123asdfasdasd__.\dataset\0x07cede39f98e7ba4b8fe0728__1312"
# res = re.search(r'(\_\_\.).*(\_\_)',str)
# if res:
#     print(res)
#     print(res.start())
#     print(res.end())
#     res_final = str[:res.start()] + str[res.end():]
#     print(res_final)

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