import re
import networkx as nx
import matplotlib.pyplot as plt

import calculate as cal
from baseBlock import BasicBlock
from checkUnit import CheckUnit

caller_address = "0x0000000000000000000000005b38da6a701c568545dcfcb03fcb875f56beddc4"
                
call_data_size = "0x0000000000000000000000000000000000000000000000000000000000000024"

call_data_load = "0x0000000000000000000000000000000000000000000000000000000000000001"

call_data_address = "0x0000000000000000000000009bbfed6889322e016e0a02ee459d306fc19545d8"

creation_path = "./opcodes-creation/"

creation_postfix = ".opcodes-creation"

run_path = "./opcodes-runtime/"

run_postfix = ".opcodes-runtime"

class contract:

    def __init__(self, name):

        self.name = name

        self.storage = {} 

        self.op_dict_c = {}

        self.op_dict_r = {}

        self.value_dict_c = {}

        self.value_dict_r = {}

        self.blocks_c = []

        self.blocks_r = []

        self.edges_c = []

        self.edges_r = []
        
        self.visited = {}
        
        self.stack = []

        self.graph_dict = {}

        self.owner_key = -1

        self.owner_value = ""

        self.SP = False

        self.SSP = False

        self.STP = False

        #preprocess
        self.process()
        #check
        self.check()
        #print
        self.print_check_msg()

    def process(self):
        c_path = creation_path + self.name + creation_postfix
        r_path = run_path + self.name + run_postfix
        self.construct_cfg(c_path,self.op_dict_c,self.value_dict_c,self.blocks_c,self.edges_c)
        self.symbolic_exec(0,self.stack,self.op_dict_c,self.value_dict_c,self.edges_c,True)
        self.visited.clear()
        self.stack.clear()
        self.construct_cfg(r_path,self.op_dict_r,self.value_dict_r,self.blocks_r,self.edges_r)
        self.symbolic_exec(0,self.stack,self.op_dict_r,self.value_dict_r,self.edges_r,False)

    def construct_cfg(self,file_path,op_dict,value_dict,blocks,edges):
        op_list = []
        move_firstLine = False
        with open(file_path, 'r') as disasm_file:
            while True:
                line = disasm_file.readline()
                if not move_firstLine:
                    move_firstLine = True
                    continue  
                if not line:
                    break
                str_list = line.split(' ')
                str_pc = str_list[0]
                pc = str_pc.replace(":", "", 1)
                pc = int(pc, 16)
                #pc = int(pc)
                opcode = str_list[1].strip()

                if opcode == "Missing":
                    opcode = "INVALID"
                if opcode == "KECCAK256":
                    opcode = "SHA3"
                if opcode == "opcode":
                    opcode = "INVALID"

                op_dict[pc] = opcode
                if len(str_list) > 2 and opcode != "INVALID":
                    str_value = str_list[-1].strip()
                    value_dict[pc] = str_value

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
            if(op_list[-1]['depart'] == False):
                op_dp = {}
                op_dp['depart'] = True
                op_list.append(op_dp)

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

    def symbolic_exec(self,tag,stack,op_dict,value_dict,edges,ctag):

        if self.visited.__contains__(tag):
            return
        block = self.get_block(tag,ctag)
        if not block:
            return
        self.visited[tag] = True
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
            elif op_code == "CALLDATASIZE":
                stack.insert(0,call_data_size)
                ins = ins + 1
            elif op_code == "CALLDATALOAD":
                if len(stack) > 0:
                    stack.pop(0)
                    stack.insert(0, call_data_load)
                    ins = ins + 1
            elif op_code == "POP":
                if len(stack) > 0:
                    stack.pop(0)
                    ins = ins + 1
            elif op_code == "CALLER":
                stack.insert(0,caller_address)
                check_unit = CheckUnit(op_code,ins)
                check_unit.set_caller_address(caller_address)
                block.add_checkUnit(check_unit)
                ins = ins + 1
            elif op_code == "EQ":
                if len(stack) > 1:
                    first = stack.pop(0)
                    second = stack.pop(0)
                    check_unit = CheckUnit(op_code,ins)
                    check_unit.set_eq(first,second)
                    block.add_checkUnit(check_unit)
                    res = cal.compute_EQ(first,second)
                    stack.insert(0, res)
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
                    res = cal.compute_SUB(first,second)
                    stack.insert(0,res)
                    ins = ins + 1
            elif op_code == "ADD":
                if len(stack) > 1:
                    first = stack.pop(0)
                    second = stack.pop(0)
                    res = cal.compute_ADD(first,second)
                    stack.insert(0,res)
                    ins = ins + 1
            elif op_code == "EXP":
                if len(stack) > 1:
                    base = stack.pop(0)
                    up = stack.pop(0)
                    res = cal.compute_EXP(base,up)
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
            elif op_code == "SHR":
                if len(stack) > 1:
                    shift = stack.pop(0)
                    value = stack.pop(0)
                    res = cal.compute_SHR(shift,value)
                    stack.insert(0,res)
                    ins = ins + 1
            elif op_code == "SHL":
                if len(stack) > 1:
                    shift = stack.pop(0)
                    value = stack.pop(0)
                    res = cal.compute_SHL(shift,value)
                    stack.insert(0,res)
                    ins = ins + 1
            elif op_code == "REVERT":
                if len(stack) > 1:
                    stack.pop(0)
                    stack.pop(0)
                ins = ins + 1
            elif op_code == "JUMP":
                if len(stack) > 1:
                    target = int(stack.pop(0),16)
                    if not self.visited.__contains__(target):
                        blockE = self.get_block(target,ctag)
                        block.set_jump_to(target)
                        edge_info = {}
                        edge_info[block.get_start_address()] = blockE.get_start_address()
                        edges.append(edge_info)
                        stackNext = stack.copy()
                        self.symbolic_exec(target,stackNext,op_dict,value_dict,edges,ctag)
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
                    res = cal.compute_LT(left,right)
                    stack.insert(0,res)
                ins = ins + 1
            elif op_code == "GT":
                if len(stack) > 1:
                    left = stack.pop(0)
                    right = stack.pop(0)
                    res = cal.compute_GT(left,right)
                    stack.insert(0,res)
                ins = ins + 1
            elif op_code == "ISZERO":
                if len(stack) > 0:
                    value = stack.pop(0)
                    res = cal.compute_ISZERO(value)
                    stack.insert(0, res)
                    ins = ins + 1
            elif op_code == "SLT":
                left = stack.pop(0)
                right = stack.pop(0)
                res = cal.compute_SLT(left,right)
                stack.insert(0, res)
                ins = ins + 1
            elif op_code == "MUL":
                multiplicand = stack.pop(0)
                multiplier = stack.pop(0)
                res = cal.compute_MUL(multiplicand,multiplier)
                stack.insert(0,res)
                ins = ins + 1
            elif op_code == "DIV":
                dividend = stack.pop(0)
                divisor = stack.pop(0)
                res = cal.compute_DIV(dividend,divisor)
                stack.insert(0, res)
                ins = ins + 1
            elif op_code == "NOT":
                oringinal = stack.pop(0)
                res = cal.compute_NOT(oringinal)
                stack.insert(0,res)
                ins = ins + 1
            elif op_code == "AND":
                and1 = stack.pop(0)
                and2 = stack.pop(0)
                res = cal.compute_AND(and1,and2)
                stack.insert(0, res)
                ins = ins + 1
            elif op_code == "OR":
                or1 = stack.pop(0)
                or2 = stack.pop(0)
                res = cal.compute_OR(or1,or2)
                stack.insert(0, res)
                ins = ins + 1
            elif op_code == "INVALID":
                ins = ins + 1
            elif op_code == "ADDRESS":
                stack.insert(0,call_data_address)
                ins = ins + 1
            elif op_code == "BALANCE":
                address = stack.pop(0)
                stack.insert(0,"0x125985")
                ins = ins + 1
            elif op_code == "RETURNDATASIZE":
                stack.insert(0, "0x24")
                ins = ins + 1
            elif op_code == "RETURNDATACOPY":
                stack.pop(0)
                stack.pop(0)
                stack.pop(0)
                ins = ins + 1
            elif op_code == "MSTORE":
                if len(stack) > 1:
                    offset = int(stack.pop(0),16)
                    value_hex = stack.pop(0)
                    # 将value_hex转为str，并且补全至64位，高位补0，转list
                    # memory[offset:offset+32] = value
                    # for i in range(offset * 2, offset * 2 + 64):
                    #     if i < len(memory):
                    #         memory[i] = value_hex[i - offset * 2]
                    #     else:
                    #         memory.append(value_hex[i - offset * 2])
                    # for i in range(math.ceil(len(memory)/64) * 64 - len(memory)):
                    #     memory.append('0')
                    ins = ins + 1
            elif op_code == "MLOAD":
                if len(stack) > 0:
                    offset = int(stack.pop(0),16)
                    # value_hex = memory[offset * 2:offset * 2 + 64]
                    stack.insert(0, "0x0")
                    ins = ins + 1
            elif op_code == "SELFDESTRUCT":
                if len(stack) > 0:
                    addr = stack.pop(0)
                    ins = ins + 1
            elif op_code == "SSTORE":
                if len(stack) > 1:
                    key = stack.pop(0)
                    value = stack.pop(0)
                    check_unit = CheckUnit(op_code,ins)
                    check_unit.set_sstore(key,value)
                    block.add_checkUnit(check_unit)
                    self.storage[key] = value
                    ins = ins + 1
            elif op_code == "SLOAD":
                if len(stack) > 0:
                    key = stack.pop(0)
                    check_unit = CheckUnit(op_code,ins)
                    if key in self.storage.keys():
                        value = self.storage[key]
                        check_unit.set_sload(key,value)
                        stack.insert(0, value)
                    else:
                        check_unit.set_sload(key,0)
                        stack.insert(0, "0x0")
                    block.add_checkUnit(check_unit)
                    ins = ins + 1
            elif op_code == "CALL":
                if len(stack) > 0:
                    outgas = stack.pop(0)
                    recipient = stack.pop(0)
                    transfer_amount = stack.pop(0)
                    start_data_input = stack.pop(0)
                    size_data_input = stack.pop(0)
                    start_data_output = stack.pop(0)
                    size_data_ouput = stack.pop(0)
                    stack.insert(0,"0x1")
            elif op_code == "CALLVALUE":
                stack.insert(0,"0x0")
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
                stack.insert(0, "0x29045A592007D0C246EF02C2223570DA9522D0CF0F73282C79A1BC8F0BB2C238")
                ins = ins + 1
            elif op_code == "JUMPDEST":
                ins = ins + 1
            elif op_code == "JUMPI":
                if len(stack) > 1:
                    target = int(stack.pop(0),16)
                    flag = int(stack.pop(0),16)
                    if not self.visited.__contains__(target):
                        blockE = self.get_block(target,ctag)
                        block.set_jump_to(target)
                        edge_info = {}
                        edge_info[block.get_start_address()] = blockE.get_start_address()
                        edges.append(edge_info)
                        stackNext = stack.copy()
                        self.symbolic_exec(target,stackNext,op_dict,value_dict,edges,ctag)
                    fall = block.get_fall_to()
                    if not self.visited.__contains__(fall):
                        stackNext = stack.copy()
                        self.symbolic_exec(fall,stackNext,op_dict,value_dict,edges,ctag)
                ins = ins + 1
            else:
                print("missing opcode>>>>>>>",op_code)
                ins = ins + 1
    def get_block(self,tag,ctag):
        if ctag:
            for i, block in enumerate(self.blocks_c):
                if block.get_start_address() == tag:
                    return block
        else:
            for i, block in enumerate(self.blocks_r):
                if block.get_start_address() == tag:
                    return block
                
    def visual_graph_c(self):
        G_c = nx.Graph()
        for i, block in enumerate(self.blocks_c):
            tag = block.get_start_address()
            G_c.add_node(tag)
        for j,edge in enumerate(self.edges_c):
            for frome in edge:
                G_c.add_edge(frome,edge[frome])
        nx.draw(G_c, with_labels=True)
        plt.show()

    def visual_graph_r(self):
        G_c = nx.Graph()
        for i, block in enumerate(self.blocks_r):
            tag = block.get_start_address()
            G_c.add_node(tag)
        for j,edge in enumerate(self.edges_r):
            for frome in edge:
                G_c.add_edge(frome,edge[frome])
        nx.draw(G_c, with_labels=True)
        plt.show()

    def check(self):
        self.initDfs_graph()
        if self.check_pre():
            for i, block_r in enumerate(self.blocks_r):
                if not self.check_privilege(block_r):
                    continue
                self.check_SSP(block_r)
                self.check_SP(block_r)
                self.check_STP(block_r)
        else:
            print("not check pre")
            
    # check if there is an owner = msg.sender operation in creation bytecode
    def check_pre(self):
        for i, block_c in enumerate(self.blocks_c):
            if not self.check_block_caller_storage(block_c):
                continue
            return True
        return False
    
    # specific check of if there is an owner = msg.sender operation in creation bytecode
    def check_block_caller_storage(self,block):
        checkUnits = block.get_checkUnits()
        for i,caller_unit in enumerate(checkUnits):
            if not caller_unit.get_unit_type() == "CALLER":
                continue
            for j,sstore_unit in enumerate(checkUnits):
                if not sstore_unit.get_unit_type() == "SSTORE":
                    continue
                if int(sstore_unit.get_sstore_value(),16) == int(caller_unit.get_caller_address(),16):
                    self.owner_key = sstore_unit.get_sstore_key()
                    self.owner_value = sstore_unit.get_sstore_value()
                    return True
        return False
    
    # check the run block has the owner == msg.sender condition
    def check_privilege(self,block):
        
        insList = block.get_instructions()
        caller_value = ""
        caller_ins = -1
        sload_key = ""
        sload_ins = -1

        for i, ins in enumerate(insList):
            op_code = self.op_dict_r[ins]
            if op_code != "CALLER":
                continue
            for j,run_unit in enumerate(block.get_checkUnits()):
                if not run_unit.get_unit_type() == "CALLER":
                    continue
                if not run_unit.get_unit_ins() == ins:
                    continue
                caller_value = run_unit.get_caller_address()
                caller_ins = ins
        if caller_ins == -1:
            return False
        
        for i, ins in enumerate(insList):
            op_code = self.op_dict_r[ins]
            if op_code != "SLOAD":
                continue
            for j,run_unit in enumerate(block.get_checkUnits()):
                if not run_unit.get_unit_type() == "SLOAD":
                    continue
                if not run_unit.get_unit_ins() == ins:
                    continue
                sload_key = run_unit.get_sload_key()
                if not int(sload_key,16) == int(self.owner_key,16):
                    continue
                sload_ins = ins
        if sload_ins == -1:
            return False
        
        for i, ins in enumerate(insList):
            op_code = self.op_dict_r[ins]
            if op_code != "EQ":
                continue
            for j,run_unit in enumerate(block.get_checkUnits()):
                if not run_unit.get_unit_type() == "EQ":
                    continue
                if not run_unit.get_unit_ins() == ins:
                    continue
                eq_left = run_unit.get_eq_left()
                eq_right = run_unit.get_eq_right()
                if caller_ins < sload_ins:
                    if int(self.owner_value,16) == int(eq_left,16) and int(caller_value,16) == int(eq_right,16):
                        return True
                else:
                    if int(self.owner_value,16) == int(eq_right,16) and int(caller_value,16) == int(eq_left,16):
                        return True
        return False
        
    def check_SSP(self,block):
        potential_path = self.get_potential_path(block.get_start_address())
        for k in potential_path:
            block_k = self.get_block(k,False)
            block_k_index = block_k.get_instructions()
            for i in block_k_index:
                if self.op_dict_r[i] != "SSTORE":
                    continue
                else:
                    self.SSP = True
                    return True
            return False
    
    def check_STP(self,block):
        potential_path = self.get_potential_path(block.get_start_address())
        for k in potential_path:
            block_k = self.get_block(k,False)
            block_k_index = block_k.get_instructions()
            for i in block_k_index:
                if self.op_dict_r[i] in ['CALL', 'CALLCODE', 'DELEGATECALL']:
                    self.STP = True
                    return True
                else:
                    return False 
        return False
    
    def check_SP(self,block):
        potential_path = self.get_potential_path(block.get_start_address())
        for k in potential_path:
            block_k = self.get_block(k,False)
            block_k_index = block_k.get_instructions()
            for i in block_k_index:
                if self.op_dict_r[i] != "SELFDESTRUCT":
                    continue
                else:
                    self.SP = True
                    return True       
        return False
    
    def initDfs_graph(self):
        for block in self.blocks_r:
            self.graph_dict[block.get_start_address()] = set()
            for i in self.edges_r:
                if list(i.keys())[0] == block.get_start_address():
                    self.graph_dict[block.get_start_address()].add(list(i.values())[0])


    def get_potential_path(self,tag):
        potential_path = set()
        s = [tag]
        while s:       
            vertex = s.pop()   
            if vertex not in potential_path:
                potential_path.add(vertex)
                s.extend(self.graph_dict[vertex] - potential_path)
        potential_path.remove(tag)
        return potential_path

    def print_check_msg(self):
        print("SP>>>>>>>",self.SP)
        print("SSP>>>>>>",self.SSP)
        print("STP>>>>>>",self.STP)

    # print check units
    def print_checkunits(self):
        print("creation checkunits >>>>>>>>")
        for i, block_c in enumerate(self.blocks_c):
            for j, check_unit_c in enumerate(block_c.get_checkUnits()):
                check_unit_c.print_data()
        print("runtime checkunits >>>>>>>>>")
        for i, block_r in enumerate(self.blocks_r):
            for j, check_unit_r in enumerate(block_r.get_checkUnits()):
                check_unit_r.print_data()


contract1 = contract("STP")

# contract1.visual_graph_c()
contract1.visual_graph_r()
