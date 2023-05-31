import pandas as pd
import shutil
import os

solFilePath = "./git-dataset/"
collectFilePath = "./process-dataset/"

def run():
    
    df = pd.read_excel('output10.xlsx')

    data_dict = df.to_dict(orient='records')

    for i,data in enumerate(data_dict):
        if not isinstance(data['mainContract'],str):
            continue
        if data['StackOverFlow'] == "True"
            continue
        file_name = data['address'] + "_" + data['mainContract'] + '.sol'
        search_path = search_files(solFilePath,file_name)
        if search_path == "notfind":
            print("error >>>> seach func not find")
            continue
        if not os.path.isfile(search_path):
            print("error >>>> not find file")
            continue
        shutil.copy(search_path, collectFilePath)

def search_files(folder, excelFile):
    for root, _, files in os.walk(folder):
        for file in files:
            if file == excelFile:
                return os.path.join(root, file)
    return "notfind"

run()


        



