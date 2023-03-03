import re
import networkx as nx
import math
import matplotlib.pyplot as plt

from baseBlock import BasicBlock

op_dict = {}

cut = []

op_list = []

cut_type = {}

value_dict = {}

blocks = []

edges = []

edges_sys = {}

visited = {}

memory = ['0' for i in range(64)]

storage = {}

graph_dict = {}

pc = 0

count = 0

end_pc = 0
def construct_cfg():

    global op_dict
    global value_dict
    global bolck_tag
    global blocks
    global edges
    global op_list
    with open('./opcodes/op_mem.opcodes', 'r') as disasm_file:
        while True:
            line = disasm_file.readline()
            if not line:
                break
            str_list = line.split(' ')
            str_pc = str_list[0]
            pc = str_pc.replace(":", "", 1)
            # pc = int(pc, 16)
            pc = int(pc)
            end_pc = pc
            opcode = str_list[1].strip()
            if opcode == "Missing":
                opcode = "INVALID"
            if opcode == "KECCAK256":
                opcode = "SHA3"
            op_dict[pc] = opcode
            if len(str_list) > 2:
                str_value = str_list[-1].strip()
                value = int(str_value, 16)
                value_dict[pc] = value

            if opcode == "STOP" or opcode == "JUMP" or opcode == "JUMPI" or opcode == "RETURN" or opcode == "SUICIDE" or opcode == "REVERT" or opcode == "ASSERTFAIL":
                op_ele = {}
                op_ele['pc'] = pc
                op_ele['opcode'] = opcode
                op_ele['depart'] = False
                op_list.append(op_ele)

                op_dp = {}
                op_dp['depart'] = True
                op_list.append(op_dp)
            elif opcode == "JUMPDEST":
                if op_list[op_list.__len__() - 1]['depart'] == False:
                    op_dp = {}
                    op_dp['depart'] = True
                    op_list.append(op_dp)

                op_ele = {}
                op_ele['pc'] = pc
                op_ele['opcode'] = opcode
                op_ele['depart'] = False
                op_list.append(op_ele)
            else:
                op_ele = {}
                op_ele['pc'] = pc
                op_ele['opcode'] = opcode
                op_ele['depart'] = False
                op_list.append(op_ele)
        op_dp = {}
        op_dp['depart'] = True
        op_list.append(op_dp)

        print(op_dict)
        print(value_dict)
        print(op_list)

        start_line = 0
        new_block = True

        for i,op_ele in enumerate(op_list):
            if new_block:
                block = BasicBlock(start_line)
                new_block = False
            if not op_ele['depart']:
                block.add_instruction(op_ele['pc'])
                continue
            block.set_end_address(op_list[i-1]['pc'])
            blocks.append(block)
            new_block = True
            if (i+1 < op_list.__len__()):
                start_line = op_list[i+1]['pc']
        print(blocks)
        for i,block in enumerate(blocks):
            if(op_dict[block.get_end_address()] == "JUMPI"):
                block.set_block_type("conditional")
                continue
            block.set_block_type("other")
        for i, block in enumerate(blocks):
            for j, fall_block in enumerate(blocks):
                if(block.get_block_type() == "conditional" and fall_block.get_start_address() == block.get_end_address() + 1):
                    block.set_fall_to(fall_block.get_start_address())
                    edge_info = {}
                    edge_info[block.get_start_address()] = fall_block.get_start_address()
                    edges.append(edge_info)
        print(edges)
def get_block(tag):
    for i, block in enumerate(blocks):
        if block.get_start_address() == tag:
            return block
def symbolic_exec(tag,stack):
    global edges_sys
    global visited
    if visited.__contains__(tag):
        return
    block = get_block(tag)
    if not block:
        return
    visited[tag] = True
    for i,ins in enumerate(block.get_instructions()):
        if not op_dict.__contains__(ins):
            ins = ins + 1
            continue
        op_code = op_dict[ins]
        if op_code.startswith("PUSH"):
            if value_dict.__contains__(ins):
                stack.insert(0,value_dict[ins])
            str = re.search(r"\d+", op_code).group(0)
            length = int(str)
            ins = ins + length + 1
        # elif op_code == "MSTORE":
        #     if len(stack) > 1:
        #         stack.pop(0)
        #         stack.pop(0)
        #         ins = ins + 1
        elif op_code == "CALLDATASIZE":
            stack.insert(0,20)
            ins = ins + 1
        elif op_code == "CALLDATALOAD":
            if len(stack) > 0:
                stack.pop(0)
                stack.insert(0, 20)
                ins = ins + 1
        elif op_code == "POP":
            if len(stack) > 0:
                stack.pop(0)
                ins = ins + 1
        elif op_code == "CALLER":
            stack.insert(0,1016)
            ins = ins + 1
        elif op_code == "EQ":
            if len(stack) > 1:
                first = stack.pop(0)
                second = stack.pop(0)
                # if first == second:
                #     computed = 1
                # else:
                #     computed = 0
                stack.insert(0, 1)
                ins = ins + 1
        elif op_code.startswith("DUP"):
            str = re.search(r"\d+", op_code).group(0)
            num = int(str)
            if len(stack) >= num:
                duplicate = stack[num - 1]
                stack.insert(0, duplicate)
                ins = ins + 1
        elif op_code.startswith("LOG"):
            str = re.search(r"\d+", op_code).group(0)
            num = int(str) + 2
            while num > 0:
                stack.pop(0)
                num = num - 1
            ins = ins + 1
        elif op_code == "SUB":
            if len(stack) > 1:
                first = stack.pop(0)
                second = stack.pop(0)
                computed = first -second
                stack.insert(0,computed)
                ins = ins + 1
        elif op_code == "ADD":
            if len(stack) > 1:
                first = stack.pop(0)
                second = stack.pop(0)
                computed = first + second
                stack.insert(0,computed)
                ins = ins + 1
        elif op_code == "EXP":
            if len(stack) > 1:
                base = stack.pop(0)
                up = stack.pop(0)
                res = base ** up
                stack.insert(0,res)
                ins = ins + 1
        elif op_code.startswith("SWAP"):
            str = re.search(r"\d+", op_code).group(0)
            num = int(str)
            if len(stack) > num:
                temp = stack[num]
                stack[num] = stack[0]
                stack[0] = temp
                ins = ins + 1
        # elif op_code == "MLOAD":
        #     if len(stack) > 0:
        #         offset = stack.pop(0)
        #         value = 20
        #         stack.insert(0, value)
        #         ins = ins + 1
        elif op_code == "SHR":
            if len(stack) > 1:
                shift = stack.pop(0)
                value = stack.pop(0)
                stack.insert(0,20)
                # if shift > 255:
                #     stack.insert(0, 0)
                # else:
                #     computed = value >> shift
                #     stack.insert(0, computed)
                ins = ins + 1
        elif op_code == "REVERT":
            if len(stack) > 1:
                stack.pop(0)
                stack.pop(0)
            ins = ins + 1
        elif op_code == "JUMP":
            if len(stack) > 1:
                target = stack.pop(0)
                if not visited.__contains__(target):
                    blockE = get_block(target)
                    block.set_jump_to(target)
                    edge_info = {}
                    edge_info[block.get_start_address()] = blockE.get_start_address()
                    edges.append(edge_info)
                    stackNext = stack.copy()
                    symbolic_exec(target, stackNext)
                ins = ins + 1
        elif op_code == "RETURN":
            if len(stack) > 1:
                stack.pop(0)
                stack.pop(0)
            ins = ins + 1
        elif op_code == "LT":
            if len(stack) > 1:
                left = stack.pop(0)
                right = stack.pop(0)
                # if left < right:
                #     computed = 1
                # else:
                #     computed = 0
            stack.insert(0,1)
            ins = ins + 1
        elif op_code == "GT":
            if len(stack) > 1:
                left = stack.pop(0)
                right = stack.pop(0)
                # if left > right:
                #     computed = 1
                # else:
                #     computed = 0
            stack.insert(0, 1)
            ins = ins + 1
        elif op_code == "ISZERO":
            if len(stack) > 0:
                value = stack.pop(0)
                if value == 0:
                    computed = 1
                else:
                    computed = 0
                stack.insert(0, computed)
                ins = ins + 1
        elif op_code == "SLT":
            left = stack.pop(0)
            right = stack.pop(0)
            # if left < right:
            #     computed = 1
            # else:
            #     computed = 0
            stack.insert(0, 1)
            ins = ins + 1
        elif op_code == "MUL":
            multiplicand = stack.pop(0)
            multiplier = stack.pop(0)
            res = multiplicand * multiplier
            stack.insert(0,res)
            ins = ins + 1
        elif op_code == "DIV":
            dividend = stack.pop(0)
            divisor = stack.pop(0)
            res = dividend / divisor
            stack.insert(0, res)
            ins = ins + 1
        elif op_code == "NOT":
            #取反 改下
            oringinal = stack.pop(0)
            stack.insert(0,0)
            ins = ins + 1
        elif op_code == "AND":
            # 取反 改下
            and1 = stack.pop(0)
            and2 = stack.pop(0)
            stack.insert(0, 0)
            ins = ins + 1
        elif op_code == "OR":
            # 取反 改下
            or1 = stack.pop(0)
            or2 = stack.pop(0)
            stack.insert(0, 0)
            ins = ins + 1
        elif op_code == "INVALID":
            ins = ins + 1
        elif op_code == "MSTORE":
            if len(stack) > 1:
                offset = stack.pop(0)
                value = stack.pop(0)
                value_hex = numTohexlst(value)
                # 将value_hex转为str，并且补全至64位，高位补0，转list
                # memory[offset:offset+32] = value
                for i in range(offset * 2, offset * 2 + 64):
                    if i < len(memory):
                        memory[i] = value_hex[i - offset * 2]
                    else:
                        memory.append(value_hex[i - offset * 2])
                for i in range(math.ceil(len(memory)/64) * 64 - len(memory)):
                    memory.append('0')
                ins = ins + 1
        elif op_code == "MLOAD":
            if len(stack) > 0:
                offset = stack.pop(0)
                value_hex = memory[offset * 2:offset * 2 + 64]
                value = hexlstTonum(value_hex)
                stack.insert(0, value)
                ins = ins + 1
        elif op_code == "SELFDESTRUCT":
            if len(stack) > 0:
                addr = stack.pop(0)
                ins = ins + 1
        elif op_code == "SSTORE":
            if len(stack) > 1:
                key = stack.pop(0)
                value = stack.pop(0)
                storage[key] = value
                ins = ins + 1
        elif op_code == "SLOAD":
            if len(stack) > 0:
                key = stack.pop(0)
                if key in storage.keys():
                    value = storage[key]
                    stack.insert(0, value)
                else:
                    stack.insert(0, 0)
                ins = ins + 1
        elif op_code == "CALLVALUE":
            value = 1000
            stack.insert(0,value)
            ins = ins + 1
        elif op_code == "CODECOPY":
            mem_location = stack.pop(0)
            code_from = stack.pop(0)
            no_bytes = stack.pop(0)
            ins = ins + 1
        elif op_code == "STOP":
            ins = ins + 1
        elif op_code == "SHA3":
            offset = stack.pop(0)
            size = stack.pop(0)
            stack.insert(0, 20)
            ins = ins + 1
        elif op_code == "JUMPDEST":
            ins = ins + 1
        elif op_code == "JUMPI":
            if len(stack) > 1:
                target = stack.pop(0)
                flag = stack.pop(0)
                if not visited.__contains__(target):
                    blockE = get_block(target)
                    block.set_jump_to(target)
                    edge_info = {}
                    edge_info[block.get_start_address()] = blockE.get_start_address()
                    edges.append(edge_info)
                    stackNext = stack.copy()
                    symbolic_exec(target, stackNext)
                fall = block.get_fall_to()
                if not visited.__contains__(fall):
                    stackNext = stack.copy()
                    symbolic_exec(fall,stackNext)
            ins = ins + 1
        else:
            print("missing opcode!!!!>>>>",op_code)
            ins = ins + 1
    print(edges)


#检测该块是否是涉及到owner的权限控制
def check_Pre(tag):
    block = get_block(tag)
    insList = block.get_instructions()
    length = len(insList)
    #权限控制
    check_cond = {}
    check_cond["SLOAD"] = False
    check_cond["CALLER"] = False
    check_cond["EQ"] = False
    check_cond["JUMPI"] = False

    for i, ins in enumerate(insList):
        op_code = op_dict[ins]
        if op_code == "SLOAD":
            check_cond["SLOAD"] = True
        elif op_code == "CALLER":
            check_cond["CALLER"] = True
        elif op_code == "EQ":
            check_cond["EQ"] = True
        elif op_code == "JUMPI":
            check_cond["JUMPI"] = True
        else:
            continue

    for v in check_cond.values():
        if not v:
            return 0
        continue
    return 1

def check_transfer_nowblock(tag):
    block = get_block(tag)
    insList = block.get_instructions()
    length = len(insList)
    for i, ins in enumerate(insList):
        if op_dict[ins] in ['CALL', 'CALLCODE', 'DELEGATECALL']:
            return 1
        else:
            return 0

#检测该块是否涉及内存操作
def check_StorageOperation(tag):
    block = get_block(tag)
    insList = block.get_instructions()
    length = len(insList)
    for i, ins in enumerate(insList):
        op_code = op_dict[ins]
        if op_code != "SSTORE":
            continue
        else:
            return 1

def check_SSP():
    for block in blocks:
        graph_dict[block.get_start_address()] = set()
        for i in edges:
            if list(i.keys())[0] == block.get_start_address():
                graph_dict[block.get_start_address()].add(list(i.values())[0])
    for i, block in enumerate(blocks):
        if check_Pre(block.get_start_address()) == 1:
            if check_StorageOperation(block.get_jump_to()) == 1:
                print ("SSP pattern found!")
                break

def check_Selfdestruct(tag):
    potential_path = set()
    s = [tag]
    while s:        # dfs
        vertex = s.pop()   
        if vertex not in potential_path:
            potential_path.add(vertex)
            s.extend(graph_dict[vertex] - potential_path)
    potential_path.remove(tag)
    for k in potential_path:
        block_k = get_block(k)
        block_k_index = block_k.get_instructions()
        for i in block_k_index:
            if op_dict[i] != "SELFDESTRUCT":
                continue
            else:
                return 1

def check_SP():
    for i, block in enumerate(blocks):
        if check_Pre(block.get_start_address()) == 1:
            if check_Selfdestruct(block.get_start_address()) == 1:
                print("SP pattern found!")
                break

def check_TS():
    for i, block in enumerate(blocks):
        if check_transfer_nowblock(block.get_start_address()) == 1:
               if check_StorageOperation(block.get_jump_to()) == 1: 
                   print("TS pattern found!")

def visual_graph():
    G = nx.Graph()
    for i, block in enumerate(blocks):
        tag = block.get_start_address()
        G.add_node(tag)
    for j,edge in enumerate(edges):
        for frome in edge:
            G.add_edge(frome,edge[frome])
    nx.draw(G, with_labels=True, arrows = True, arrowstyle="->")
    plt.show()

def check_Transfer(tag):
    potential_path = set()
    s = [tag]
    while s:        # dfs
        vertex = s.pop()   
        if vertex not in potential_path:
            potential_path.add(vertex)
            s.extend(graph_dict[vertex] - potential_path)
    potential_path.remove(tag)
    for k in potential_path:
        block_k = get_block(k)
        block_k_index = block_k.get_instructions()
        for i in block_k_index:
            if op_dict[i] in ['CALL', 'CALLCODE', 'DELEGATECALL']:
                continue
            else:
                return 1

def check_STP():
    for i, block in enumerate(blocks):
        if check_Pre(block.get_start_address()) == 1:
            if check_Transfer(block.get_start_address()) == 1:
                print("STP pattern found!")
                break


def numTohexlst(num):
    str = ''
    while num > 0:
        str='0123456789ABCDEF'[num%16]+str
        num=(num-num%16)//16
    l = ['0' for i in range(64-len(str))]
    l += list(str)
    return l

def hexlstTonum(t):
    s = ''
    for i in t:
        s += i
    odata = 0
    su =s.upper()
    for c in su:
        tmp=ord(c)
        if tmp <= ord('9') :
            odata = odata << 4
            odata += tmp - ord('0')
        elif ord('A') <= tmp <= ord('F'):
            odata = odata << 4
            odata += tmp - ord('A') + 10
    return odata


stack = []
construct_cfg()
symbolic_exec(0,stack)
check_SSP()
check_STP()
check_SP()
visual_graph()
