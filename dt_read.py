#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 26 08:39:58 2021

@author: mouchen
"""
import sys, os, platform

# Get current user OS
_OS = platform.system()
print("[system] OS detect: ", _OS)
if _OS == "Linux":
    COLOR_EN = 1
    print("[system] Color print support on Linux!\n")
else:
    COLOR_EN = 0
    print("[system] Color print not support on Windows!\n")

# Project sku
PROJ_NAME = "DEVICE TREE INDEX"
PROJ_VERSION = "1.0"
PROJ_RELEASE = "2021/08/26"
PROJ_VERSION = "1.1"
PROJ_RELEASE = "2021/09/16"

# Project config file
DT_CONFIG_PATH = "./config.txt"

# Define some global variables
global DTS_PATH
global DT_UNFIXED_PATH
global YAML_SEARCH_PATH
dt_arr = []
node_list = []
unfixed_file_list = []

def FileInfo():
    global PROJ_VERSION, DTS_PATH, DT_UNFIXED_PATH
    print("  + Project version: ", PROJ_VERSION)
    print("  + DTS path: ", DTS_PATH)
    print("  + DT unfixed path: ", DT_UNFIXED_PATH)

def CmdHelp():
    global PROJ_VERSION
    if _OS == "Linux":
        head_cmd = './'
    elif _OS == "Windows":
        head_cmd = ''
    print("======================================================================================================================")
    print("* Topic    : "+PROJ_NAME)
    print("* Auth     : Mouchen Hung")
    print("* Ver&Date : "+PROJ_VERSION+" "+PROJ_RELEASE)
    print("* OS       : Linux/Windows")
    print("* Command  : (O) Print all nodes                                             --> "+head_cmd+"dt_read.py")
    print("             (O) Print diagram of device tree                                --> "+head_cmd+"dt_read.py 0 0")
    print("             (O) Display dts file                                            --> "+head_cmd+"dt_read.py 0 1")
    print("             (O) Display dt unfixed file                                     --> "+head_cmd+"dt_read.py 0 2")
    print("             (O) Print certain nodes with given node ord                     --> "+head_cmd+"dt_read.py 1 <node_ord>")
    print("             (O) Print certain nodes with given node name keyword            --> "+head_cmd+"dt_read.py 2 <node_name_keyword>")
    print("             (O) Print certain nodes with given node compat keyword          --> "+head_cmd+"dt_read.py 3 <node_compat_keyword>")
    print("             (O) Print certain content with given keyword in dt unfixed file --> "+head_cmd+"dt_read.py 4 <keyword>")
    print("             (O) Print certain section with given node id in dt unfixed file --> "+head_cmd+"dt_read.py 5 <node_id>")
    print("             (O) Print certain section with given node name in dt file       --> "+head_cmd+"dt_read.py 6 <node_name>")
    print("             (O) Display certain yaml file with given keyword in binding dir --> "+head_cmd+"dt_read.py 7 <file_name_keyword>")
    print("             (O) List every yaml files in binding dir                        --> "+head_cmd+"dt_read.py 7 all")
    print("* Note     : - Only collect below node elements in NODE INFO,")
    print("               |ord|stat|path|id|label|name|compat|reg|interrupts|p_label|")
    print("             - Color print only support on Linux.")
    print("======================================================================================================================")

def COLORPRINT(STR, COLOR):
    global COLOR_EN
    if COLOR_EN:
        if(COLOR=="BLACK"):
            return "\033[1;30m" + STR +"\033[0m"
        if(COLOR=="RED"):
            return "\033[1;31m" + STR +"\033[0m"
        if(COLOR=="GREEN"):
            return "\033[1;32m" + STR +"\033[0m"
        if(COLOR=="YELLOW"):
            return "\033[1;33m" + STR +"\033[0m"
        if(COLOR=="BLUE"):
            return "\033[1;34m" + STR +"\033[0m"
        if(COLOR=="PURPLE"):
            return "\033[1;35m" + STR +"\033[0m"
        if(COLOR=="BLUE1"):
            return "\033[1;36m" + STR +"\033[0m"
        if(COLOR=="WHITE"):
            return "\033[1;37m" + STR +"\033[0m"
    else:
        return STR

def MC_PRINT(string, mode):
    if mode == "ERROR":
        header = "[ERROR] "
        color = "RED"
    elif mode == "WARN":
        header = "[WARN] "
        color = "YELLOW"
    elif mode == "SYS":
        header = "[system] "
        color = "PURPLE"
    else:
        header = "[info] "
        color = "WHITE"
        
    if COLOR_EN:
        print(COLORPRINT(header+string, color))
    else:
        print(string)

def SearchSubStringIndex(main_str, sub_str):
    end_p = len(main_str)
    start_p = 0
    find_index_arr = []
    while (end_p - start_p) >= len(sub_str):
        sub_pos = main_str.find(sub_str, start_p, end_p)
        if sub_pos == -1:
            break
        else:
            find_index_arr.append(sub_pos)
            start_p+=(len(sub_str)+sub_pos)
    return find_index_arr

def CheckFileExist(filepath):
    if os.path.exists(filepath):
        return 0
    else:   
        return 1

def PrintFile(file_path, color):
    with open(file_path) as f:
        lines = f.readlines()
        for line in lines:
            line = line.replace('\n', '')
            if COLOR_EN:
                print(COLORPRINT(line, color))
            else:
                print(line)

def DT_PathToID(node_path):
    ret = 'DT_N'
    for ele in node_path:
        if ele == '/':
            ret+='_S_'
        elif ele == '@' or ele == '-':
            ret+='_'
        elif ele == '"':
            continue
        else:
            ret+=ele.lower()
    return ret

def AddExtendContent(node_lst, ord_lst, path_lst):
    init_arr = []
    for i in range(len(node_list)):
        init_arr.append([0,0])
        
    for i in range(len(node_lst)):
        full_name = node_lst[i][2].replace('@', '_')
        full_name = full_name.replace('-', '_')
        if full_name == '/':
            full_name = "DT_N"
        keyword = full_name+"_ORD"
        for j in range(len(ord_lst)):
            
            if keyword in ord_lst[j]:
                if init_arr[j][0]:
                    continue
                node_lst[i][7] = ord_lst[j].split(' ')[2]
                init_arr[j][0] = 1
                break
            
        keyword = full_name+"_PATH"
        for j in range(len(path_lst)):
            if keyword in path_lst[j]:
                if init_arr[j][1]:
                    continue
                node_lst[i][8] = path_lst[j].split(' ')[2]
                node_lst[i][9] = DT_PathToID(node_lst[i][8])
                init_arr[j][1] = 1
                break
            
    return node_lst

def BeautiPrint(node, mode):
    if mode == 0:
        print("* [ord] ", node[7])
        print("* [stat] ", node[0])
        print("* [path] ", node[8])
        print("* [id] ", node[9])
        print("* [label] ", node[1])
        print("* [name] ", node[2])
        print("* [compat] ", node[3])
        print("* [reg] ", node[4])
        print("* [interupts] ", node[5])
        print("* [p_label] ", node[6])
        print('')
    else:
        print(("* [ord] "+node[7]).ljust(12, ' '), end='')
        print((", [id] "+node[9]).ljust(50, ' '), end='')
        print((", [stat] "+node[0]).ljust(10, ' '), end='')
        print((", [label] "+node[1]).ljust(35, ' '), end='')
        print((", [name] "+node[2]).ljust(35, ' '), end='')
        print((", [compat] "+node[3]).ljust(35, ' '), end='')
        
        print((",\n  [path] "+node[8]).ljust(60, ' '), end='')
        print((", [reg] "+node[4]).ljust(35, ' '), end='')
        print((", [interupts] "+node[5]).ljust(35, ' '), end='')
        print((", [p_label] "+node[6]).ljust(20, ' '), end='')
        print('\n')

def DT_CheckConfigfile():
    global PROJ_VERSION, DT_CONFIG_PATH, DTS_PATH, DT_UNFIXED_PATH, YAML_SEARCH_PATH
    
    if DT_CONFIG_PATH == "":
        MC_PRINT("Error in define DT_CONFIG_PATH in code!", "ERROR")
        return 1
    else:
        if CheckFileExist(DT_CONFIG_PATH):
            MC_PRINT("Config file is missing, please asking 'config.txt' from provider.", "ERROR")
            return 1
        else:
            MC_PRINT("Config file catch success!", "SYS")
            with open(DT_CONFIG_PATH) as f:
                lines = f.readlines()
                for line in lines:
                    line = line.replace(' ', '')
                    line = line.replace('\n', '')
                    line = line.replace('"', '')
                    if "//" in line or "/*" in line or "*/" in line:
                        continue
                    elif "VERSION" in line:
                        if line.split('=')[1] != PROJ_VERSION:
                            MC_PRINT("VERSION of config file is not correspond to CODE_VERSION "+PROJ_VERSION, "ERROR")
                            return 1
                    elif "DTS_FILE_PATH" in line:
                        DTS_PATH = line.split('=')[1]
                    elif "DT_UNFIXED_FILE_PATH" in line:
                        DT_UNFIXED_PATH = line.split('=')[1]
                    elif "YAML_SEARCH_PATH" in line:
                        YAML_SEARCH_PATH = line.split('=')[1]
                        
    return 0

def DT_GetStatus(key, mode):
    global node_list
    
    if mode == "BYNAME":
        for i in range(len(node_list)):
            if key.lower() in node_list[i][2].lower():
                return node_list[i][0]
    elif mode == "BYORD":
        for i in range(len(node_list)):
            if key.lower() in node_list[i][7].lower():
                return node_list[i][0]
    
    return "error"
        
def DT_Plot(dts_path):
    global dt_arr
    
    dt_arr = []
    level = 0
    with open(dts_path) as f:
        lines = f.readlines()
        for line in lines:
            if '{' in line:
                line = line.replace('{', '')
                line = line.replace('\n', '')
                line = line.replace('\t', '')
                line = line.replace(' ', '')
                if ':' in line:
                    line = line.split(':')[1]
                dt_arr.append([line, level])
                level+=1
            if '}' in line:
                level-=1
    
    print("\n{ Device Tree based on Root }")
    last_level = 0
    for node in dt_arr:
        if COLOR_EN:
            node_stat = DT_GetStatus(node[0], "BYNAME")
            if node_stat == "O":
                node_color = "GREEN"
            elif node_stat == "X":
                node_color = "RED"
            else:
                node_color = "WHITE"
            
        node_name = '['+node[0]+']'
        if node[0] == '/':
            if COLOR_EN:
                print(COLORPRINT(node_name, node_color).ljust(16, ' '), end='')
            else:
                print(node_name.ljust(5, ' '), end='')
            continue
        if node[1] == last_level:
            print("")
            for i in range(node[1]):
                if i == 0:
                    print("|    ", end='')
                    continue
                print("|                             ", end='')
            if COLOR_EN:
                print(COLORPRINT(node_name, node_color).ljust(41, ' '), end='')
            else:
                print(node_name.ljust(30, ' '), end='')
        else:
            if node[1] > last_level:
                if COLOR_EN:
                    print(COLORPRINT(node_name, node_color).ljust(41, ' '), end='')
                else:
                    print((node_name).ljust(30,' '), end='')
            else:
                print("")
                for i in range(node[1]):
                    if i == 0:
                        print("|    ", end='')
                        continue
                    print("|                             ", end='')
                if COLOR_EN:
                    print(COLORPRINT(node_name, node_color).ljust(41, ' '), end='')
                else:
                    print((node_name).ljust(30,' '), end='')
        last_level = node[1]
    if COLOR_EN:
        print("\n")
        print("--------------------------------------------------------")
        print(COLORPRINT("[status] okay", "GREEN"))
        print(COLORPRINT("[status] disabled", "RED"))
        print(COLORPRINT("[status] not defined(regard as 'okay' in unfixed header)", "WHITE"))
        print("--------------------------------------------------------")
    print("")

def DT_GetDTSNodeSection(node_name, dts_file):
    color_select = "BLUE"
    rec_flag = 0
    level_flag = 0
    with open(dts_file) as f:
        lines = f.readlines()
        for line in lines:
            line = line.replace('\n', '')
            if rec_flag:
                if '}' in line:
                    level_flag-=1
                if '{' in line:
                    level_flag+=1
                    
                if COLOR_EN:
                    print(COLORPRINT(line, color_select))
                else:
                    print(line)
                    
                if not level_flag:
                    print("")
                    rec_flag = 0
            
            if node_name.lower() in line.lower() and '{' in line:
                if COLOR_EN:
                    print(COLORPRINT(line, color_select))
                else:
                    print(line)
                rec_flag = 1
                level_flag = 1
                continue

def DT_FindYAML(search_path, keyword, mode):
    keyword = keyword.lower()
    key_base = "aspeed,"
    result_arr = []
    for root, dirs, files in os.walk(search_path, topdown=False):
        for name in files:
            cur_file = os.path.join(root, name)
            if '.yaml' or '.yml' in cur_file:
                if key_base in cur_file:
                    result_arr.append(cur_file)
    if mode == "SINGLE":
        find_list=[]
        for ele in result_arr:
            if keyword in ele:
                find_list.append(ele)
        if len(find_list) == 0:
            return ""
        if len(find_list) == 1:
            return find_list[0]
        MC_PRINT("You got "+str(len(find_list))+" result with keyword "+keyword+", please select 1 file below:", "INFO")
        for i in range(len(find_list)):
            print(" ["+str(i+1)+"] "+find_list[i])
        while(1):
            select = input("Select index above: ")
            try:
                s_index = int(select)
            except:
                MC_PRINT("Only accept int variable!", "WARN")
                continue
            if s_index<=0 or s_index>len(find_list):
                MC_PRINT("Out of index!", "WARN")
            else:
                return find_list[s_index-1]
    elif mode == "LISTALL":
        return result_arr
    
    return ""

'''
class flag:
    [1] ord list
    [2] node section
'''
def DT_UnfixedNodeSectionFind(file, class_print_lst, keyword):
    with open(file) as f:
        lines = f.readlines()
        
        catch_flag = 0
        rec_flag = 0
        read_flag = 0
        class_flag = 0
        rec_arr = []
        content_arr = []
        for line in lines:
            line = line.replace('\n', '')
            
            if read_flag:
                if "Node identifier" in line:
                    for i in range(0, len(content_arr)-3):
                        if '/*' in content_arr[i] and '*/' in content_arr[i]:
                            if content_arr[i][0] == '/':
                                if COLOR_EN:
                                    print(COLORPRINT(content_arr[i], "BLUE"))
                                    continue
                        print(content_arr[i])
                    #print("-----------------------------------------------------")
                    rec_flag = 1
                    class_flag = 2
                    rec_arr.append(content_arr[-3])
                    rec_arr.append(content_arr[-2])
                    rec_arr.append(content_arr[-1])
                    rec_arr.append(line)
                    read_flag = 0
                    content_arr = []
                    
                elif "* Chosen nodes" in line:
                    for i in range(0, len(content_arr)-1):
                        print(content_arr[i])
                    #print("-----------------------------------------------------")
                    rec_flag = 1
                    class_flag = 3
                    rec_arr.append(content_arr[-1])
                    rec_arr.append(line)
                    read_flag = 0
                    content_arr = []
                    
                else:
                    content_arr.append(line)
                    
                continue
                
            if '/*' in line and '*/' not in line:
                rec_flag = 1
                rec_arr.append(line)
            elif '*/' in line and '/*' not in line:
                rec_flag = 0
                rec_arr.append(line)
                if len(rec_arr) > 1:
                    for ele in class_print_lst:
                        if ele == class_flag:
                            if keyword.lower() == "all":
                                catch_flag = 1
                                for ele in rec_arr:
                                    print(ele)
                                read_flag = 1
                            else:
                                key_flag = 0
                                for ele in rec_arr:
                                    if "Node identifier:" in ele and keyword.lower() == ele.split(': ')[1].lower():
                                        catch_flag = 1
                                        key_flag = 1
                                        break
                                if key_flag:
                                    for ele in rec_arr:
                                        print(ele)
                                    read_flag = 1
                            break
                        
                rec_arr = []
                class_flag = 0
            else:
                if rec_flag:
                    rec_arr.append(line)
                    if "Node dependency ordering" in line:
                        class_flag = 1
                    elif "Node identifier" in line:
                        class_flag = 2
                    elif "* Chosen nodes" in line:
                        class_flag = 3
                    elif "* Chosen nodes" in line:
                        class_flag = 4
                    elif '* Macros for compatibles with status "okay" nodes' in line:
                        class_flag = 5
                    elif '* Macros for status "okay" instances of each compatible' in line:
                        class_flag = 6
    return catch_flag

def DT_Catch(dts_path, dt_unfixed):
    global node_list, unfixed_file_list
    
    # status, label, name, compat, reg, inter, p_label, ord, path, id
    data = ['', '', '' ,'' , '', '', '', '', '', '']
    record = 0
    with open(dts_path) as f:
        lines = f.readlines()
        for line in lines:
            if '#' in line:
                continue
            
            elif '{' in line:
                if record:
                    node_list.append([data[0], data[1], data[2], data[3], data[4], data[5], data[6], '', '', ''])
                data = ['','','','','','','']
                line = line.replace('{', '')
                line = line.replace('\t', '')
                line = line.replace('\n', '')
                line = line.replace(' ', '')
                if ':' in line:
                    data[1] = line.split(':')[0]
                    data[2] = line.split(':')[1]
                else:
                    data[1] = ''
                    data[2] = line
                
                record = 1
            elif '}' in line:
                if record:
                    node_list.append([data[0], data[1], data[2], data[3], data[4], data[5], data[6], '', '', ''])
                    record = 0
            
            else:
                if record == 1:
                    if 'status' in line:
                        if 'okay' in line:
                            line = "O"
                        else:
                            line = "X"
                        data[0] = line;
                    elif 'compatible' in line:
                        line = line.replace('compatible = ', '')
                        line = line.replace(';', '')
                        line = line.replace('\t', '')
                        line = line.replace('\n', '')
                        data[3] = line;
                    elif 'reg' in line and 'reg-name' not in line:
                        line = line.replace('reg = ', '')
                        line = line.replace(';', '')
                        line = line.replace('\t', '')
                        line = line.replace('\n', '')
                        data[4] = line;
                    elif 'interrupts' in line:
                        line = line.replace('interrupts = ', '')
                        line = line.replace(';', '')
                        line = line.replace('\t', '')
                        line = line.replace('\n', '')
                        data[5] = line;
                    elif 'label' in line:
                        line = line.replace('label = ', '')
                        line = line.replace(';', '')
                        line = line.replace('\t', '')
                        line = line.replace('\n', '')
                        data[6] = line;
    
    ord_list = []
    path_list = []
    unfixed_file_list = []
    with open(dt_unfixed) as f:
        lines = f.readlines()
        for line in lines:  
            unfixed_file_list.append(line.replace('\n', ''))
            if '_ORD' in line and '_ORDS' not in line:
                line = line.replace('\n', '')
                ord_list.append(line)
            elif '_PATH' in line:
                line = line.replace('\n', '')
                path_list.append(line)
                
    #Check for length of ord and path list

    extend_content_check = 0
    if len(ord_list) != len(node_list):
        MC_PRINT("Length of ord_list("+str(len(ord_list))+") not equal node_list("+str(len(path_list))+")!", "ERROR")
        extend_content_check = 1
        
    if len(path_list) != len(node_list):
        MC_PRINT("Length of path_list("+str(len(path_list))+") not equal node_list("+str(len(path_list))+")!", "ERROR")
        extend_content_check = 1
    
    if not extend_content_check:
        MC_PRINT("Extend content checked!", "SYS")
        AddExtendContent(node_list, ord_list, path_list)    

            
if __name__ == '__main__':
    select_catch = 0
    select_node_key = '-1'
    select_mode = -1
    
    MC_PRINT("Parsing config file...", "SYS")
    if DT_CheckConfigfile():
        sys.exit(0)
    else:
        MC_PRINT("Project info:", "SYS")
        FileInfo()
    
    if CheckFileExist(DTS_PATH):
        MC_PRINT("DTS file not existed!", "ERROR")
        sys.exit(0)
    if CheckFileExist(DT_UNFIXED_PATH):
        MC_PRINT("devicetree_unfixed.h file not existed!", "ERROR")
        sys.exit(0)
    
    MC_PRINT("DT files checked!", "SYS")
    
    if len(sys.argv) != 3 and len(sys.argv) != 1:
        MC_PRINT("User command error, please check again command list!!", "ERROR")
        CmdHelp()
        sys.exit(0)
        
    else:
        if len(sys.argv) == 1:
            MC_PRINT("Print all nodes in DTS.\n", "SYS")
        else:
            if sys.argv[1] == '0':
                MC_PRINT("Plot diagram of DTS.\n", "SYS")
                select_node_key = sys.argv[2]
                select_mode = 0
            elif sys.argv[1] == '1':
                MC_PRINT("Print node info with ord ["+sys.argv[2]+"] in DTS.\n", "SYS")
                select_node_key = sys.argv[2]
                select_mode = 1
            elif sys.argv[1] == '2':
                MC_PRINT("Print node info with name_keyword ["+sys.argv[2]+"] in DTS.\n", "SYS")
                select_node_key = sys.argv[2]
                select_mode = 2
            elif sys.argv[1] == '3':
                MC_PRINT("Print node info with compat_keyword ["+sys.argv[2]+"] in DTS.\n", "SYS")
                select_node_key = sys.argv[2]
                select_mode = 3
            elif sys.argv[1] == '4':
                MC_PRINT("Print content with keyword ["+sys.argv[2]+"] in devicetree_unfixed.h.\n", "SYS")
                select_node_key = sys.argv[2]
                select_mode = 4
            elif sys.argv[1] == '5':
                MC_PRINT("Print section with node_id ["+sys.argv[2]+"] in devicetree_unfixed.h.\n", "SYS")
                select_node_key = sys.argv[2]
                select_mode = 5
            elif sys.argv[1] == '6':
                MC_PRINT("Print section with node_name ["+sys.argv[2]+"] in zephyr.dts.\n", "SYS")
                select_node_key = sys.argv[2]
                select_mode = 6
            elif sys.argv[1] == '7':
                MC_PRINT("Display file with file keyword ["+sys.argv[2]+"] in bindings dir.\n", "SYS")
                select_node_key = sys.argv[2]
                select_mode = 7
            else:
                MC_PRINT("User command error, please check again command list!!", "ERROR")
                CmdHelp()
                sys.exit(0)
    
    MC_PRINT("Data collecting...", "SYS")
    DT_Catch(DTS_PATH, DT_UNFIXED_PATH)
    
    # General mode
    if select_mode == 0:
        if select_node_key == '0':
            MC_PRINT("Diagram plot", "SYS")
            DT_Plot(DTS_PATH)
            
        elif select_node_key == '1':
            MC_PRINT("Display file dts:", "SYS")
            print("\n{ Device Tree Zephyr.dts }")
            PrintFile(DTS_PATH, "WHITE")
                        
        elif select_node_key == '2':
            MC_PRINT("Display file dt unfixed:", "SYS")
            print("\n{ Device Tree devicetree_unfixed.h }")
            PrintFile(DT_UNFIXED_PATH, "WHITE")

        else:
            MC_PRINT("Invalid mode selected!", "ERROR")
            sys.exit(0)
        
        print("")
        MC_PRINT("You could also type command bellow:", "SYS")
        CmdHelp()
        sys.exit(0)
        
    elif select_mode == 5:
        MC_PRINT("Start scaning...", "SYS")
        if not DT_UnfixedNodeSectionFind(DT_UNFIXED_PATH, [1,2], select_node_key):
            MC_PRINT("Can't find any content with given node_id.", "ERROR")
        MC_PRINT("End of scaning...", "SYS")
        MC_PRINT("You could also type command bellow:", "SYS")
        CmdHelp()
        sys.exit(0)
        
    elif select_mode == 6:
        MC_PRINT("Search result:", "SYS")
        DT_GetDTSNodeSection(select_node_key, DTS_PATH)
        print("")
        MC_PRINT("You could also type command bellow:", "SYS")
        CmdHelp()
        sys.exit(0)
    
    elif select_mode == 7:
        if select_node_key.lower() == "all":
            MC_PRINT("List all yaml file:", "SYS")
            yaml_path_arr = DT_FindYAML(YAML_SEARCH_PATH, "", 'LISTALL')
            
            if len(yaml_path_arr):
                for ele in yaml_path_arr:
                    if COLOR_EN:
                        print(COLORPRINT(ele, "YELLOW"))
                    else:
                        print(ele)
            else:
                MC_PRINT("Can't find any yaml file in "+YAML_SEARCH_PATH, "WARN")
        else:
            MC_PRINT("Display certain yaml file:", "SYS")
            yaml_path = DT_FindYAML(YAML_SEARCH_PATH, select_node_key.lower(), 'SINGLE')
            if yaml_path == "":
                MC_PRINT("Can't find any yaml file with keyword", "WARN")
            else:
                print("\n{ Device Tree yaml file "+yaml_path+" }")
                PrintFile(yaml_path, "BLUE")
            
        print("")
        MC_PRINT("You could also type command bellow:", "SYS")
        CmdHelp()
        sys.exit(0)
        
    else:
        MC_PRINT("Data list below...\n", "SYS")
        if select_mode!=4:
            for node in node_list:
                if select_mode == 1 and node[7]!=select_node_key:
                    continue
                if select_mode == 2 and select_node_key.lower() not in node[2].lower():
                    continue
                if select_mode == 3 and select_node_key.lower() not in node[3].lower():
                    continue
                
                if select_mode == -1:
                    BeautiPrint(node, 1)
                else:
                    BeautiPrint(node, 0)
                select_catch = 1
                
            if select_mode == 1 and not select_catch:
                MC_PRINT("Can't find node with given ord!", "WARN")
            elif select_mode == 2 and not select_catch:
                MC_PRINT("Can't find node with given name_keyword!", "WARN")
            elif select_mode == 3 and not select_catch:
                MC_PRINT("Can't find node with given compat_keyword!", "WARN")
                
            print("\nTotal nodes: ", len(node_list))
    
        else:
            for line in unfixed_file_list:
                if select_node_key.lower() in line.lower():
                    if COLOR_EN:
                        print(COLORPRINT("@search-engine: ~#\n", "BLUE1"), line)
                    else:
                        print("@search-engine: ~#\n", line)
                    select_catch = 1
            print("")
            if select_mode == 4 and not select_catch:
                MC_PRINT("Can't find any content with given keyword!", "WARN")
        
        print("")
        MC_PRINT("You could also type command bellow:", "SYS")
        CmdHelp()