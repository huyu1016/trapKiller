import os
import re
from solcx import install_solc

solFilePath = "./git-dataset/"

solcVersionPath = "C:\\Users\\18813\\Documents\\.solcx\\"

list_dirs = os.walk(solFilePath)
version_set = set()

def check_version(version):
    list_dirs = os.walk(solcVersionPath)
    for _,dirs,_ in list_dirs:
        for dir in dirs:
            version_list = dir.split('v')
            hasversion = version_list[1].strip()
            if version == hasversion:
                return True
            continue
    return False

def preprocess():
    for root,_,files in list_dirs:
        for f in files:
            file_path = os.path.join(root,f)
            with open(file_path,'r',encoding='utf-8') as disasm_file:
                while True:
                    line = disasm_file.readline().strip()
                    if not line:
                        break
                    pattern = re.compile(r'pragma solidity')
                    if re.search(pattern, line):
                        detail_pattern = r"\^?(\d+\.\d+\.\d+)"
                        match = re.search(detail_pattern, line)
                        if match:
                            version = match.group(1).strip()
                            version_set.add(version)
                        break
                    else:
                        continue
    for version in version_set:
        numlist = version.split('.')
        pre = int(numlist[1].strip())
        pro = int(numlist[2].strip())
        if pre == 4 and pro < 11:
            version = "0.4.25"
        if not check_version(version):
            print(version)
            try:
                install_solc(version)
            except:
                print("version")
preprocess()