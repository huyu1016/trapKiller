import re
from nltk.stem import PorterStemmer
import requests
import pandas as pd
import shutil
import os

# solFilePath = "./git-dataset/00/00A0a01fef5A3210ea387BA725F0F9cA91BfE4DD_ARTSEETOKEN.sol"
# solFilePath = "./sol/SP.sol"
collectFilePath = "./process-dataset/"
originFilePath = "./git-dataset/"
cleanFilePath = "./clean-dataset/"

syns = ['bankroll', 'capitalize', 'endow', 'fund', 'stake', 'subsidize', 'underwrite']
related_words = ['grubstake','cofinance','refinance','advocate','aid','stand','establish',
'back','champion','endorse','patronize','sponsor','pay','organize','award','draw','deposit',
'support','maintain','nourish','discharge','receive']
Defi_words = ['interest', 'lend', 'p2p', 'loan', 'credit', 'reward', 'bonus','ERC','token','mint']

world_word = []

#1.将智能合约按照标点符号和空格进行分割：这一步是将智能合约文本根据标点符号和空格进行分割，得到一个单词列表。
#  这里的目的是将合约文本分解成离散的单词，以便进行后续处理。通常，标点符号和空格本身不包含有意义的信息，因此将它们用作分割依据。

#2.根据驼峰命名法分离单词：对于使用驼峰命名法的单词，例如"moneyLending"，根据驼峰规则将其分离成多个单词，
#  即"money"和"Lending"。这样做是为了更好地处理合约中的复合词，以便提取更准确的含义。

#3.使用词干提取器转换单词形式：通过使用Porter词干提取器，将单词转换为其词干形式。
#  例如，将"lending"替换为"lend"。词干提取可以减少不同形式的单词对后续分析的影响，将它们归一化为通用形式。

#4.判断DeFi相关合约：最后，根据合约中是否包含与金融相关的关键词，判断合约是否与DeFi（去中心化金融）相关。
#  如果合约包含预定义的金融关键词，就将其视为DeFi相关合约。这一步是为了筛选出与DeFi领域相关的合约进行后续的分析和处理。

#5.根据韦氏词典和智能合约总结的单词去匹配分割成单词的合约，如果能够匹配上就认为是Defi

def split_contract_into_words(contract_text):

    # #匹配到左右括号()插入一个空格
    # contract_text = re.sub(r'([()])', r' \1 ', contract_text)

    # #匹配到左右方括号[]插入一个空格
    # contract_text = re.sub(r'(\[|\])', r' \1 ', contract_text)

    # #匹配到点.替换插入一个空格
    # contract_text = re.sub(r'(\[|\])', r' \1 ', contract_text)

    # 移除特殊字符标点符号 括号等
    contract_text =  re.sub(r'[^\w\s]', ' ', contract_text)
    
    # 按空格分割
    words = contract_text.split()
    
    # 去除空单词
    words = [word for word in words if word]

    #去除_
    words = [word for word in words if word != "_"]

    #分离驼峰单词组
    for index,word in enumerate(words):
        process_words = split_camel_case(word)
        words = words + process_words
        words.remove(word)

    #去掉数字
    words = [word for word in words if not word.isdigit()]

    #使用Porter词干提取器，将单词转换为其词干 存疑
    # for index,word in enumerate(words):
    #     new_word = stem_word(word)
    #     if new_word == word:
    #         continue
    #     words[index] = new_word

    
    #去重
    words = list(set(words))

    return words

def split_camel_case(word):

    # 使用正则表达式分离驼峰命名的单词
    # words = re.findall(r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))', word)
    # words = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', word)
    words = re.findall(r'[A-Z]?[a-z\d]+|[A-Z\d]+(?=[A-Z]|$)', word)
    # print(words)
    return words

def remove_comments(contract_text):
    
    # 去除单行注释
    contract_text = re.sub(r'//.*', '', contract_text)
    
    # 去除多行注释
    contract_text = re.sub(r'/\*.*?\*/', '', contract_text, flags=re.DOTALL)
    
    return contract_text

def stem_word(word):
    stemmer = PorterStemmer()
    stemmed_word = stemmer.stem(word)
    return stemmed_word

def is_Defi(words):
    for word in words:
        for pattern in syns:
            if word_match(word,pattern):
                msg = "match: " + pattern
                write_msg(msg)
                return True
        for pattern in related_words:
            if word_match(word,pattern):
                msg = "match: " + pattern
                write_msg(msg)
                return True
        for pattern in Defi_words:
            if word_match(word,pattern):
                msg = "match: " + pattern
                write_msg(msg)
                return True
    return False

def contract_process():
    global world_word
    for root, _, files in os.walk(collectFilePath):
        for f in files:
            file_path = os.path.join(root, f)
            with open(file_path,"r",encoding='utf-8') as file:
                print("process file: " + f)
                contract_text = file.read()
                contract_text = remove_comments(contract_text)
                words = split_contract_into_words(contract_text)
                if  is_Defi(words):
                    if os.path.isfile(file_path):
                        shutil.copy(file_path, cleanFilePath)
                else:
                    msg = "mismatch" + f
                    write_msg(msg)
            world_word = world_word + words
            world_word = list(set(world_word))
    write_msg(str(world_word))

def getRelatedWords():
    # api_key = "63a8e38e-077b-4918-a658-6937cd9abaeb"
    request_url = "https://www.dictionaryapi.com/api/v3/references/thesaurus/json/finance?key=63a8e38e-077b-4918-a658-6937cd9abaeb"
    response = requests.get(request_url)
    if response.status_code == 200:
        # 解析 JSON 响应
        json_data = response.json()
        print(json_data['meta']['syns'])
    else:
        print("Failed to retrieve data.")


def word_match(word,pattern):
    matches = re.findall(pattern, word, re.IGNORECASE)
    return len(matches) > 0

def filter_contract():

    df = pd.read_excel('output12.xlsx')

    data_dict = df.to_dict(orient='records')

    for i,data in enumerate(data_dict):
        if not isinstance(data['mainContract'],str):
            continue
        if data['StackOverFlow'] == True:
            continue
        file_name = data['address'] + "_" + data['mainContract'] + '.sol'
        search_path = search_files(originFilePath,file_name)
        if search_path == "notfind":
            msg = file_name + " not find file"
            write_msg(msg)
            continue
        if not os.path.isfile(search_path):
            msg = file_name + " no file"
            write_msg(msg)
            continue
        shutil.copy(search_path, collectFilePath)

def search_files(folder, excelFile):
    for root, _, files in os.walk(folder):
        for file in files:
            if file == excelFile:
                return os.path.join(root, file)
    return "notfind"

def write_msg(msg):
    with open("./process.log",'a') as f:
        f.write(msg)
        f.write('\n')
        f.close()

def cleanLog():
    with open("./process.log",'w') as f:
        f.flush()
        f.close()
   
def cleanFolder():
    if os.path.exists(collectFilePath):
        shutil.rmtree(collectFilePath)
    os.mkdir(collectFilePath)

def run():
    cleanLog()
    contract_process()

def filter():
    cleanFolder()
    filter_contract()


run()

# filter()

# filter_contract()


# [{'meta': {'id': 'finance', 'uuid': '331839aa-3d37-4a00-9c40-1d3eaa680d16', 'src': 'coll_thes', 'section': 'alpha', 'target': {'tuuid': 'cc250bde-c35e-4a8b-9463-f60a8e16670d', 'tsrc': 'collegiate'}, 'stems': ['finance', 'financed', 'finances', 'financing'], 'syns': [['bankroll', 'capitalize', 'endow', 'fund', 'stake', 'subsidize', 'underwrite'], ['endow', 'fund', 'subsidize']], 'ants': [['defund'], ['defund', 'disendow']], 'offensive': False}, 'hwi': {'hw': 'finance'}, 'fl': 'verb', 'def': [{'sseq': [[['sense', {'sn': '1', 'dt': [['text', 'to provide money for '], ['vis', [{'t': "a local business kindly {it}financed{/it} the high school band's trip to New York City"}]]], 'syn_list': [[{'wd': 'bankroll'}, {'wd': 'capitalize'}, {'wd': 'endow'}, {'wd': 'fund'}, {'wd': 'stake'}, {'wd': 'subsidize'}, {'wd': 'underwrite'}]], 'rel_list': [[{'wd': 'grubstake'}], [{'wd': 'cofinance'}, {'wd': 'refinance'}], [{'wd': 'advocate'}, {'wd': 'aid'}, {'wd': 'back'}, {'wd': 'champion'}, {'wd': 'endorse', 'wvrs': [{'wvl': 'also', 'wva': 'indorse'}]}, {'wd': 'patronize'}, {'wd': 'sponsor'}, {'wd': 'support'}], [{'wd': 'maintain'}, {'wd': 'nourish'}, {'wd': 'provide (for)'}], [{'wd': 'clear'}, {'wd': 'defray'}, {'wd': 'discharge'}, {'wd': 'foot'}, {'wd': 'liquidate'}, {'wd': 'pay'}, {'wd': 'pay off'}, {'wd': 'pay up'}, {'wd': 'quit'}, {'wd': 'recompense'}, {'wd': 'settle'}, {'wd': 'spring (for)'}, {'wd': 'stand'}], [{'wd': 'refund'}]], 'ant_list': [[{'wd': 'defund'}]]}]], [['sense', {'sn': '2', 'dt': [['text', 'to furnish (as an institution) with a regular source of income '], ['vis', [{'t': 'established a fund to {it}finance{/it} a visiting lecturer position at the local college'}]]], 'syn_list': [[{'wd': 'endow'}, {'wd': 'fund'}, {'wd': 'subsidize'}]], 'rel_list': [[{'wd': 'establish'}, {'wd': 'found'}, {'wd': 'organize'}], [{'wd': 'bequeath'}, {'wd': 'contribute'}, {'wd': 'donate'}, {'wd': 'subscribe'}, {'wd': 'support'}, {'wd': 'underwrite'}], [{'wd': 'award'}, {'wd': 'grant'}], [{'wd': 'back'}, {'wd': 'promote'}, {'wd': 'sponsor'}], [{'wd': 'capitalize'}, {'wd': 'invest (in)'}]], 'near_list': [[{'wd': 'draw'}, {'wd': 'receive'}], [{'wd': 'subsist'}]], 'ant_list': [[{'wd': 'defund'}, {'wd': 'disendow'}]]}]]]}], 'shortdef': ['to provide money for', 'to furnish (as an institution) with a regular source of income']}]

# print(stem_word("decrease"))
# res = split_camel_case("IERC20Token")
# print(res)
# getRelatedWords()

# print(word_match('aERC20','erc'))
# words = ['fudnddds','jiang']
# print(is_Defi(words))

# 1.是否用poter词根
# 2.单词数量 不对 
# 3.匹配原则是什么