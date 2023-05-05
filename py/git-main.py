import os
import re
import time
import shutil
import json
import pandas as pd

from label import Label
from contract import contract


solFilePath = "./git-dataset/"

solcVersionPath = "C:\\Users\\yafei\\.solcx\\"

excelData = {}

binProcess = "./process/"
astPath = "./ast/"
bin_full = "./bin-full/"
bin_run = "./bin-runtime/"
bin_creation = "./bin-creation/"

opcodes_runtime = "./opcodes-runtime/"
opcodes_creation = "./opcodes-creation/"


def getMainContractName(fileName):
    command_json = "solc --ast-compact-json " + solFilePath + fileName + " -o " + astPath
    os.system(command_json)
    with open(astPath + fileName + "_json.ast", 'r', encoding='utf-8') as f:
        contents = json.load(f)

def handleAst(fileName,mainContractName,contract,solcCmd,jsonChose):
    
    command_json = solcCmd + jsonChose + solFilePath + fileName + " -o " + astPath
    os.system(command_json)

    if not os.path.isfile(astPath + fileName + "_json.ast"):
        return False
   
    with open(astPath + fileName + "_json.ast", 'r', encoding='utf-8') as f:
        contents = json.load(f)
        idList = contents["exportedSymbols"]
        idInfo = contents["nodes"]

        MainContractNodeId = idList[mainContractName][0]
        AllNodesId = [i[0] for i in list(idList.values())]

        AllDependencies = {}
        for (index, info) in enumerate(idInfo):
            if info['nodeType'] != "ContractDefinition":
                continue
            AllDependencies[info['id']] = info['contractDependencies']
            if info['id'] == MainContractNodeId:
                MainContractDependencies = info['contractDependencies']
        s = MainContractDependencies
        visited = []
        
        while s:
            temp = s.pop(0)
            if temp in visited:
                continue
            visited.append(temp)
            for i in AllDependencies[temp]:
                s.insert(0, i)
      
        visited.append(MainContractNodeId)
        AllMainContractDependencies = set(visited)
        if set(AllNodesId) == AllMainContractDependencies:
            contract.set_FT(False)
            return
        notDependedId = set(AllNodesId) - AllMainContractDependencies
        # notDependedId.add(MainContractNodeId)
      
        for info in idInfo:
            if info['id'] not in notDependedId:
                continue
            if info['nodeType'] != "ContractDefinition":
                continue
            for funcInfo in info['nodes']:
                if funcInfo['nodeType'] != "FunctionDefinition":
                    continue
                if "payable" not in funcInfo.keys() or funcInfo['payable'] != True:
                    continue
                if funcInfo['body'] is None or funcInfo['body']['statements'] is None:
                    continue
                for statemnent in funcInfo['body']['statements']:
                    # 检测主体
                    if not recur_statement(statemnent,fileName):
                        continue
                    contract.set_FT(True)
    return True
       
def recur_statement(statement,fileName):
    if statement['nodeType'] == "ExpressionStatement":
        if check_expression(statement):
            return True
        else:
            return False
    if statement['nodeType'] == "IfStatement":
        if not statement['falseBody'] is None:
            if statement['falseBody']['nodeType'] == "Block":
                for statement_recur in statement['falseBody']['statements']:
                    recur_statement(statement_recur,fileName)
            else:
                recur_statement(statement['falseBody'],fileName)
        if not statement['trueBody'] is None:
            if statement['trueBody']['nodeType'] == "Block":
                for statement_recur in statement['trueBody']['statements']:
                    recur_statement(statement_recur,fileName)
            else:
                recur_statement(statement['trueBody'],fileName)
    elif statement['nodeType'] == "ForStatement":
        if statement['body']['nodeType'] == "Block":
            for statement_recur in statement['body']['statements']:
                recur_statement(statement_recur,fileName)
        else:
            recur_statement(statement['body'])
    elif statement['nodeType'] == "WhileStatement":
        if statement['body']['nodeType'] == "Block":
            for statement_recur in statement['body']['statements']:
                recur_statement(statement_recur,fileName)
        else:
             recur_statement(statement['body'],fileName)
    elif statement['nodeType'] == "Return":
        return check_expression(statement)
    else:
        if statement['nodeType'] != "VariableDeclarationStatement" and  statement['nodeType'] != "EmitStatement" and statement['nodeType'] != "Throw" and statement['nodeType'] != "Break" and statement['nodeType'] != "InlineAssembly":
            msg = "missing statement type" + statement['nodeType'] + fileName
            write_msg(msg)
        return False

def check_expression(expressionInfo):

    if expressionInfo['expression'] is None:
        return False
    if 'nodeType' not in expressionInfo['expression'].keys():
        return False
    if expressionInfo['expression']['nodeType'] is None:
        return False
    if expressionInfo['expression']['nodeType'] != "FunctionCall":
        return False
    if expressionInfo['expression']['expression']['nodeType'] != "MemberAccess":
        return False
    expressionType = expressionInfo['expression']['expression']['memberName']
    if expressionType == "transfer" or expressionType == "send" or expressionType == "value":
        return True
    return False

def getVersion(path):
    with open(path,'r',encoding='utf-8') as disasm_file:
        while True:
            line = disasm_file.readline()
            if line == '':
                break
            pattern = re.compile(r'pragma solidity')
            if re.search(pattern, line):
                detail_pattern = r"\^?(\d+\.\d+\.\d+)"
                match = re.search(detail_pattern, line)
                if match:
                    return match.group(1).strip()
                break
            else:
                continue
    return "mismatch"

def handle():
    addressList = list()
    mainContractList = list()
    TSList = list()
    SPList = list()
    SSPList = list()
    STPList = list()
    FTList = list()
    StackOverflowList = list()
    list_dirs = os.walk(solFilePath)
    for _,_,files in list_dirs:
        for f in files:    
            str_list = f.split('_')
            address = str_list[0]
            last_str = str_list[1].strip()
            mainContractName = last_str.split('.')[0].strip()

            fileName = f
            fileFullName = mainContractName + ".bin"
            fileRunName = mainContractName + ".bin-runtime"
            fileCreationName = mainContractName + ".bin-creation"
            opcodesRunName = mainContractName + ".opcodes-runtime"
            opcodesCreationName = mainContractName + ".opcodes-creation"

            version = getVersion(solFilePath + fileName)
            if version == "mismatch":
                write_msg("version not match"+fileName)
                continue
            
            solcCmd = solcVersionPath + "solc-v" + version + "\\" + "solc.exe"
            command_full = solcCmd + " --bin " + solFilePath + fileName + " -o " + binProcess
            if not os.path.isfile(solFilePath + fileName):
                write_msg("no sol file")
                continue
            
            os.system(command_full)
            fileList = os.listdir(binProcess)
            for f_name in fileList:
                if f_name !=  fileFullName:
                    os.remove(binProcess + f_name)

            
            originName = binProcess + fileFullName
            if not os.path.isfile(originName):
                write_msg("compile error " + fileName)
                continue
            if os.path.isfile(bin_full + fileFullName):
                os.remove(bin_full + fileFullName)

            shutil.move(originName,bin_full)

            command_run = solcCmd + " --bin-runtime " + solFilePath + fileName + " -o " + binProcess
            os.system(command_run)
            fileList = os.listdir(binProcess)
            for f_name in fileList:
                if f_name != fileRunName:
                    os.remove(binProcess + f_name)
            originName = binProcess + fileRunName

            if os.path.isfile(bin_run + fileRunName):
                os.remove(bin_run + fileRunName)

            shutil.move(originName,bin_run)
        

            with open(bin_full + fileFullName,'r',encoding='utf-8') as f:
                str_full = f.read()
                f.close()
            with open(bin_run + fileRunName,'r',encoding='utf-8') as f:   
                str_run = f.read()
                f.close()
            creation = str_full[:len(str_full)-len(str_run)]
            with open(bin_creation + fileCreationName,'w',encoding='utf-8') as f:   
                f.write(creation)
                f.close()


            libraryHandel(bin_run + fileRunName)

            command_evm_run = "evm disasm " + bin_run + fileRunName + " > " + opcodes_runtime + opcodesRunName
            os.system(command_evm_run)
            
            command_evm_creation = "evm disasm " + bin_creation + fileCreationName + " > " + opcodes_creation + opcodesCreationName
            os.system(command_evm_creation)


            contract_anlysis = contract(mainContractName)

            jsonChose = " --ast-compact-json "
            numlist = version.split('.')
            pre = int(numlist[1].strip())
            pro = int(numlist[2].strip())
            if pre == 4 and pro <= 11:
                jsonChose = " --ast-json "
                write_msg("low version " + fileName)
                continue
                
            res = handleAst(fileName,mainContractName,contract_anlysis,solcCmd,jsonChose)
            if not res:
                write_msg("ast error " + fileName)
                continue
            
            addressList.append(address)
            mainContractList.append(mainContractName)
            TSList.append(contract_anlysis.get_TS())
            SPList.append(contract_anlysis.get_SP())
            SSPList.append(contract_anlysis.get_SSP())
            STPList.append(contract_anlysis.get_STP())
            FTList.append(contract_anlysis.get_FT())
            StackOverflowList.append(contract_anlysis.get_overflow())
            contract_anlysis.__del__()


    excelData['address'] = addressList
    excelData['mainContract'] = mainContractList
    excelData['TS'] = TSList
    excelData['SP'] = SPList
    excelData['SSP'] = SSPList
    excelData['STP'] = STPList
    excelData['FT'] = FTList
    excelData['StackOverFlow'] = StackOverflowList

    df = pd.DataFrame(excelData)

    df.to_excel('output.xlsx', index=False)

def libraryHandel(file_path):

    with open(file_path,'r') as f:
        str = f.read()
        res = re.search(r'(\_\_\.).*(\_\_)',str)
        if res:
            res_final = str[:res.start()] + str[res.end():]
            f.close()
            with open(file_path,'w') as w:
                w.write(res_final)
                w.close()
        else:
            f.close()

def print_res():
    print("dadasd")

def cleanAll():

    if os.path.exists(bin_full):
        shutil.rmtree(bin_full)
    os.mkdir(bin_full)
    if os.path.exists(bin_creation):
        shutil.rmtree(bin_creation)
    os.mkdir(bin_creation)
    if os.path.exists(bin_run):
        shutil.rmtree(bin_run)
    os.mkdir(bin_run)
    if os.path.exists(opcodes_runtime):
        shutil.rmtree(opcodes_runtime)
    os.mkdir(opcodes_runtime)
    if os.path.exists(opcodes_creation):
        shutil.rmtree(opcodes_creation)
    os.mkdir(opcodes_creation)
    if os.path.exists(astPath):
        shutil.rmtree(astPath)
    os.mkdir(astPath)

    if os.path.isfile("./output.xlsx"):
        os.remove("./output.xlsx")

def cleanLog():
    with open("./error.log",'w') as f:
        f.flush()
        f.close()

def write_msg(msg):
    with open("./error.log",'a') as f:
        f.write(msg)
        f.write('\n')
        f.close()
        
def run():

    start = time.time()

    cleanAll()

    cleanLog()

    # handle()

    end = time.time()

    print(f"running time: {end - start} s")


run()

# # cleanAll()

# # cleanLog()

# # handle()