import json
from contract import contract
from compile_test import get_all_contracts
import os
all_contracts = get_all_contracts()
# 需要构建CCG，找出mainContract所依赖的所有contractNodeId
for contract in all_contracts:
    ContractName = contract.get_name()
    print(ContractName)
    MainContractName = contract.get_main_contr()
    ast_NI_path = './ast-NI/' + ContractName + '.ast-NI'
    ast_CN_path = './ast-CN/' + ContractName + '.ast-CN'
    with open(ast_CN_path, 'r') as f:
        contractName2nodeId = json.load(f)
    with open(ast_NI_path, "r", encoding="utf-8") as f:
        nodesInfo = json.load(f)
    MainContractNodeId = contractName2nodeId[MainContractName][0]
    AllNodesId = [i[0] for i in list(contractName2nodeId.values())]
    # print(AllNodesId)
    AllDependencies = {}
    for (index, i) in enumerate(nodesInfo):
        if index == 0:
            AllDependencies[1] = []
            continue
        AllDependencies[i['id']] = i['contractDependencies']
        if i['id'] == MainContractNodeId:
            MainContractDependencies = i['contractDependencies']
    s = MainContractDependencies
    visited = []
    while s:
        temp = s.pop(0)
        if temp in visited:
            continue
        visited.append(temp)
        for i in AllDependencies[temp]:
            s.insert(0, i)
    AllMainContractDependencies = set(visited)
    if set(AllNodesId) == AllMainContractDependencies:
        # print('All contracts/libraries used!!!!!!!!!')
        continue
    else:
        NotDependedId = list(set(AllNodesId) - set(AllMainContractDependencies) - {MainContractNodeId})
        # print(NotDependedId)
    NotDependedContract = []
    for i in NotDependedId:
        for j in contractName2nodeId:
            if i == contractName2nodeId[j][0]:
                NotDependedContract.append(j)
    Json_path = './json/' + ContractName + '.json'
    with open(Json_path, 'r', encoding='utf-8') as f:
        contents = json.load(f)
    filepath = "./0/" + ContractName + ".sol"
    for i in NotDependedContract:
        path = filepath + ":" + i
        bin = contents[path]['bin']
        bin_runtime = contents[path]['bin-runtime']
        bin_creation = bin[:len(bin)-len(bin_runtime)]
        creation_output_path = './temp/temp.creation'
        command_creation = "echo -n " + bin_creation +" | evmasm -d -o " + creation_output_path
        os.system(command_creation)
        runtime_output_path = './temp/temp.runtime'
        command_runtime = "echo -n " + bin_runtime +" | evmasm -d -o " + runtime_output_path
        os.system(command_runtime)
        # creation路径: './temp/temp.creation'
        # runtime路径: './temp/temp.runtime'
        # 接下来只需要将两个文件的路径作为参数输入到main函数中，执行相关检测
        # main(creation_output_path, runtime_output_path)