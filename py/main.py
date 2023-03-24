import os
import re
import time
import shutil
from label import Label
from contract import contract

labels = []
solFilePath = "./dataset/"
binProcess = "./process/"
bin_full = "./bin-full/"
bin_run = "./bin-runtime/"
bin_creation = "./bin-creation/"

opcodes_runtime = "./opcodes-runtime/"
opcodes_creation = "./opcodes-creation/"

contract_sum = 0

SSP_label_sum = 0
SSP_evaluate_TP = 0
SSP_evaluate_TN = 0
SSP_evaluate_FP = 0
SSP_evaluate_FN = 0

TS_label_sum = 0
TS_evaluate_TP = 0
TS_evaluate_TN = 0
TS_evaluate_FP = 0
TS_evaluate_FN = 0

STP_label_sum = 0
STP_evaluate_TP = 0
STP_evaluate_TN = 0
STP_evaluate_FP = 0
STP_evaluate_FN = 0

SP_label_sum = 0
SP_evaluate_TP = 0
SP_evaluate_TN = 0
SP_evaluate_FP = 0
SP_evaluate_FN = 0


def processLabel():
    with open("./labeled.txt", encoding='utf-8') as f:
        contents = f.readlines()
        begin = 0
        while(begin < contents.__len__()):

            main_line = begin 
            mainContent = contents[main_line].split('======')[1]
            fileName = mainContent.split(',')[0]
            mainContractName = mainContent.split(',')[1]

            labelUnit = Label(fileName)
            labelUnit.setMainContractName(mainContractName)

            ts_line = begin + 1
            tsFlag = False
            tsContent = contents[ts_line].split(':')
            if tsContent[0].strip() != "Tricky Send":
                print("parse error>>>>",ts_line)
                break
            tsFlagStr = tsContent[1].split(' ')[1].strip()
            if tsFlagStr == "true":
                tsFlag = True
            elif tsFlagStr == "false":
                tsFlag = False
            else: 
                print("parse error>>>>",ts_line)
                break
            
            labelUnit.setLabelTS(tsFlag)

            ssp_line = begin + 2
            sspFlag = False
            sspContet = contents[ssp_line].split(':')
            if sspContet[0].strip() != "Super Storage Permission":
                print("parse error>>>>",ssp_line)
                break
            sspFlagStr = sspContet[1].split(' ')[1].strip()
            if sspFlagStr == "true":
                sspFlag = True
            elif sspFlagStr == "false":
                sspFlag = False
            else: 
                print("parse error>>>>",ssp_line)
                break
            
            labelUnit.setLabelSSP(sspFlag)

            stp_line = begin + 3
            stpFlag = False
            stpContet = contents[stp_line].split(':')
            if stpContet[0].strip() != "Super Transfer Permission":
                print("parse error>>>>",stp_line)
                break
            stpFlagStr = stpContet[1].split(' ')[1].strip()
            if stpFlagStr == "true":
                stpFlag = True
            elif stpFlagStr == "false":
                stpFlag = False
            else: 
                print("parse error>>>>",stp_line)
                break

            labelUnit.setLabelSTP(stpFlag)

            sp_line = begin + 4
            spFlag = False
            spContet = contents[sp_line].split(':')
            if spContet[0].strip() != "Self Destruct Permission":
                print("parse error>>>>",sp_line)
                break
            spFlagStr = spContet[1].split(' ')[1].strip()
            if spFlagStr == "true":
                spFlag = True
            elif spFlagStr == "false":
                spFlag = False
            else: 
                print("parse error>>>>",sp_line)
                break

            labelUnit.setLabelSP(spFlag)

            ft_line = begin + 5

            labels.append(labelUnit)
            
            begin = begin + 6
    f.close()

def handleLabel():
    
    global contract_sum

    for labelUnit in labels:

        fileName = labelUnit.getFileName() + ".sol"
        fileFullName = labelUnit.getMainContractName() + ".bin"
        fileRunName = labelUnit.getMainContractName() + ".bin-runtime"
        fileCreationName = labelUnit.getMainContractName() + ".bin-creation"

        opcodesRunName = labelUnit.getMainContractName() + ".opcodes-runtime"
        opcodesCreationName = labelUnit.getMainContractName() + ".opcodes-creation"

        command_full = "solc --bin " + solFilePath + fileName + " -o " + binProcess

        if not os.path.isfile(solFilePath + fileName):
            continue

        os.system(command_full)
        fileList = os.listdir(binProcess)
        for f_name in fileList:
            if f_name != labelUnit.getMainContractName() + ".bin":
                os.remove(binProcess + f_name)
        originName = binProcess + fileFullName

        if os.path.isfile(bin_full + fileFullName):
            os.remove(bin_full + fileFullName)

        shutil.move(originName,bin_full)

        command_run = "solc --bin-runtime " + solFilePath + fileName + " -o " + binProcess
        os.system(command_run)
        fileList = os.listdir(binProcess)
        for f_name in fileList:
            if f_name != labelUnit.getMainContractName() + ".bin-runtime":
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

        contract_anlysis = contract(labelUnit.getMainContractName())
        
        contract_sum = contract_sum + 1

        handleFlagTS(labelUnit.getLabelTS(),contract_anlysis.get_TS(),labelUnit.getMainContractName())
        handleFlagSSP(labelUnit.getLabelSSP(),contract_anlysis.get_SSP(),labelUnit.getMainContractName())
        handleFlagSTP(labelUnit.getLabelSTP(),contract_anlysis.get_STP(),labelUnit.getMainContractName())
        handleFlagSP(labelUnit.getLabelSP(),contract_anlysis.get_SP(),labelUnit.getMainContractName())

        contract_anlysis.__del__()


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

def handleFlagTS(label,contract,fileName):

    global TS_label_sum
    global TS_evaluate_FN
    global TS_evaluate_TP
    global TS_evaluate_FP
    global TS_evaluate_TN

    if label:
        TS_label_sum = TS_label_sum + 1
        if not contract:
            write_msg(fileName + " TS>>FN")
            TS_evaluate_FN = TS_evaluate_FN + 1
        else:
            TS_evaluate_TP = TS_evaluate_TP + 1
    if not label:
        if contract:
            write_msg(fileName + " TS>>FP")
            TS_evaluate_FP = TS_evaluate_FP + 1
        else:
            TS_evaluate_TN = TS_evaluate_TN + 1

def handleFlagSSP(label,contract,fileName):

    global SSP_label_sum
    global SSP_evaluate_FN
    global SSP_evaluate_TP
    global SSP_evaluate_FP
    global SSP_evaluate_TN

    if label:
        SSP_label_sum = SSP_label_sum + 1
        if not contract:
            write_msg(fileName + " SSP>>FN")
            SSP_evaluate_FN = SSP_evaluate_FN + 1
        else:
            SSP_evaluate_TP = SSP_evaluate_TP + 1
    if not label:
        if contract:
            write_msg(fileName + " SSP>>FP")
            SSP_evaluate_FP = SSP_evaluate_FP + 1
        else:
            SSP_evaluate_TN = SSP_evaluate_TN + 1

def handleFlagSTP(label,contract,fileName):

    global STP_label_sum
    global STP_evaluate_FN
    global STP_evaluate_TP
    global STP_evaluate_FP
    global STP_evaluate_TN

    if label:
        STP_label_sum = STP_label_sum + 1
        if not contract:
            write_msg(fileName + " STP>>FN")
            STP_evaluate_FN = STP_evaluate_FN + 1
        else:
            STP_evaluate_TP = STP_evaluate_TP + 1
    if not label:
        if contract:
            write_msg(fileName + " STP>>FP")
            STP_evaluate_FP = STP_evaluate_FP + 1
        else:
            STP_evaluate_TN = STP_evaluate_TN + 1
            
def handleFlagSP(label,contract,fileName):

    global SP_label_sum
    global SP_evaluate_FN
    global SP_evaluate_TP
    global SP_evaluate_FP
    global SP_evaluate_TN

    if label:
        SP_label_sum = SP_label_sum + 1
        if not contract:
            write_msg(fileName + " SP>>FN")
            SP_evaluate_FN = SP_evaluate_FN + 1
        else:
            SP_evaluate_TP = SP_evaluate_TP + 1
    if not label:
        if contract:
            write_msg(fileName + " SP>>FP")
            SP_evaluate_FP = SP_evaluate_FP + 1
        else:
            SP_evaluate_TN = SP_evaluate_TN + 1

def print_res():
    print("TS>>>",TS_label_sum,TS_evaluate_TP,TS_evaluate_TN,TS_evaluate_FP,TS_evaluate_FN)
    print("SSP>>>",SSP_label_sum,SSP_evaluate_TP,SSP_evaluate_TN,SSP_evaluate_FP,SSP_evaluate_FN)
    print("STP>>>",STP_label_sum,STP_evaluate_TP,STP_evaluate_TN,STP_evaluate_FP,STP_evaluate_FN)
    print("SP>>>",SP_label_sum,SP_evaluate_TP,SP_evaluate_TN,SP_evaluate_FP,SP_evaluate_FN)


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

    processLabel()

    handleLabel()

    print_res()

    end = time.time()

    print(f"running time: {end - start} s")

cleanAll()