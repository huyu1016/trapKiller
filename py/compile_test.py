import solcx
import re
import os
import json
import contract
def get_all_contracts():
    contracts = []
    with open("./0/labeled.txt", encoding='utf-8') as f:
        contents = f.readlines()
        for i in range(500):
            first_line = ''
            for j in contents[i*6].split(' '):
                first_line += j
            name = contents[i*6][6:48]
            main_contract = first_line[49: len(first_line)-9]
            boolean = True if contents[i*6][-2] == 'Y' else False
            ts = True if contents[i*6+1][13:17] == 'true' else False
            ssp = True if contents[i*6+2][26:30] == 'true' else False
            stp = True if contents[i*6+3][27:31] == 'true' else False
            sp = True if contents[i*6+4][26:30] == 'true' else False
            ft = True if contents[i*6+5][17:21] == 'true' else False
            Contract = contract(name, main_contract, boolean, ts, ssp, stp, sp, ft)
            contracts.append(Contract)
    all_sol_files = set(os.listdir('./0'))
    all_sol_files_exist = list(set([i.get_name() + ".sol" for i in contracts]) & all_sol_files)
    contracts_filtered = []
    for i in contracts:
        if i.get_name()+".sol" in all_sol_files_exist and i.get_boolean():
            contracts_filtered.append(i)
    return contracts_filtered
contracts_filtered = get_all_contracts()
for items in contracts_filtered:
    filepath = "./0/" + items.get_name() + ".sol"
    # with open(filepath, encoding='utf-8') as f:
    #     source = f.readlines()
    #     for i in source:
    #         if i[:6] == "pragma":
    #             temp = i.split()
    #             for j in temp:
    #                 if "^" in j or ">" in j:
    #                     version = re.findall(r'[0-9]+\.[0-9]+\.[0-9]+',j)[0]
    #             break
    res = solcx.compile_files([filepath],solc_version='0.4.25')
    mainpath = filepath+":"+items.get_main_contr()
    bin = res[mainpath]['bin']
    bin_runtime = res[mainpath]['bin-runtime']
    bin_creation = bin[:len(bin)-len(bin_runtime)]
    ast = res[mainpath]['ast']
    bin_runtime_path = "./bin-runtime/"+ items.get_name() + ".bin-runtime"
    bin_full_path = "./bin-full/"+ items.get_name() + ".bin"
    bin_creation_path = "./bin-creation/"+ items.get_name() + ".bin-creation"
    ast_CN_path = "./ast-CN/" + items.get_name() + ".ast-CN"
    ast_NI_path = "./ast-NI/" + items.get_name() + ".ast-NI"
    with open(bin_runtime_path, 'w') as f:
        f.write(bin_runtime)
    with open(bin_full_path, 'w') as f:
        f.write(bin)
    with open(bin_creation_path, 'w') as f:
        f.write(bin_creation)
    with open(ast_CN_path, 'w') as f:
        contractName2nodeId = json.dumps(ast['exportedSymbols'])
        f.write(contractName2nodeId)
    with open(ast_NI_path, 'w') as f:
        nodesInfo = json.dumps(ast['nodes'])
        f.write(nodesInfo)
def WriteFiles(ipath,opath):
    command = "evmasm -d -i " + ipath + " -o " + opath
    os.system(command)
for i in contracts_filtered:
    bin_runtime_path = "./bin-runtime/" + i.get_name() + ".bin-runtime"
    opcodes_runtime_path = "./opcodes-runtime/" + i.get_name() + ".opcodes-runtime"
    WriteFiles(bin_runtime_path,opcodes_runtime_path)
    bin_full_path = "./bin-full/" + i.get_name() + ".bin"
    opcodes_full_path = "./opcodes-full/" + i.get_name() + ".opcodes"
    WriteFiles(bin_full_path,opcodes_full_path)
    bin_creation_path = "./bin-creation/" + i.get_name() + ".bin-creation"
    opcodes_creation_path = "./opcodes-creation/" + i.get_name() + ".opcodes-creation"
    WriteFiles(bin_creation_path,opcodes_creation_path)
