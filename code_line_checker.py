from io import TextIOWrapper
import sys
import re
import os
import json
# 检查if的正则表达式
if_re = re.compile(r'\s*if\s+.*\s*:\s*') # 要用+号！
# 检查for的正则表达式
for_re = re.compile(r'\s*for\s+.*\s+in\s+.*\s*:\s*')
# 检查while的正则表达式
while_re = re.compile(r'\s*while\s+.*\s*:\s*')
# 检查try的正则表达式
try_re = re.compile(r'\s*try\s*:\s*')
# 检查变量定义的正则表达式
var_re = re.compile(r'\s*.*\s*=\s*.*\s*')

def command_lines_checker(file: TextIOWrapper, isPy: bool = False):
    total_lines = 0
    comment_lines = 0
    blank_lines = 0
    func_line_dict = {}
    max_indent = 0
    if_count = 0
    for_count = 0
    while_count = 0
    try_count = 0
    var_count = 0

    data_list = file.readlines()
    total_lines = len(data_list)

    if isPy:
        # 中间变量
        _current_func = None
        _current_func_line = 0
        for i in data_list:
            # 注释
            if i.strip().startswith('#'):
                comment_lines += 1
            # 空行
            elif i.strip() == '':
                blank_lines += 1
            # 函数
            elif i.strip().startswith('def'):
                _func_name = i.strip()[3:len(i)-1]
                if _current_func != _func_name:
                    # 新的函数
                    if _current_func is not None:
                        func_line_dict[_current_func] = _current_func_line
                    _current_func = _func_name
                    _current_func_line = 0
            else:
                # 检查缩进数
                indent = 0
                for j in i:
                    if j == ' ':
                        indent += 1
                    else:
                        break
                if indent > max_indent:
                    max_indent = indent
            
            # 检查if
            if if_re.match(i):
                if_count += 1
            # 检查for
            if for_re.match(i):
                for_count += 1
            # 检查while
            if while_re.match(i):
                while_count += 1
            # 检查try
            if try_re.match(i):
                try_count += 1
            # 检查变量定义
            if var_re.match(i):
                var_count += 1
            
            if _current_func is not None:
                _current_func_line += 1

        if _current_func is not None:
            func_line_dict[_current_func] = _current_func_line
    res = {}
    res['total_lines'] = total_lines
    res['comment_lines'] = comment_lines
    res['blank_lines'] = blank_lines
    res['code_lines'] = total_lines - comment_lines - blank_lines
    res['func_line_dict'] = func_line_dict
    res['max_indent'] = max_indent
    res['if_count'] = if_count
    res['for_count'] = for_count
    res['while_count'] = while_count
    res['try_count'] = try_count
    res['var_count'] = var_count
    res['is_py'] = isPy
    res['file_name'] = file.name
    return res

def get_all_file_names(path):
    # 得到文件夹下的所有文件路径
    file_paths = []
    for root, dirs, files in os.walk(path):
        for file in files:
            file_paths.append(os.path.join(root, file))
    return file_paths

def write_to_file(file_name, data):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("result file: " + i + 'result.json')

if __name__ == '__main__':
    # 得到参数
    args = sys.argv[1:]
    for i in args:
        print(i)
        # 检查是否是文件夹，如果是的话，则只统计.py文件，且得到文件夹下（包含子文件夹）的所有py文件
        if i.endswith('\\'):
            # 是文件夹
            total_list = [] # 用于存放所有文件的统计结果
            # 得到文件夹下的所有文件
            file_names = get_all_file_names(i)
            for j in file_names:
                if j.endswith('.py'):
                    with open(j, 'r', encoding='utf-8') as f:
                        # print("file name: " + f.name)
                        total_list.append(command_lines_checker(f, True))
            # 汇总结果
            total_dict = {}
            max_intent = 0
            for k in total_list:
                for key, value in k.items():
                    if key not in total_dict:
                        # 初始化键值对和一些特判
                        if key == 'func_line_dict':
                            total_dict['func_line_dict'] = {
                                k['file_name']: value
                            }
                        elif key == 'file_name':
                            total_dict['file_name'] = [value]
                        elif key == 'is_py':
                            total_dict['is_py'] = True
                        elif key == 'max_indent':
                            if value > max_intent:
                                max_intent = value
                            total_dict['max_indent'] = max_intent
                        else:
                            total_dict[key] = value
                    else:
                        # 汇总和一些特判，如max_indent：取最大值而不是相加
                        if key == 'func_line_dict':
                            total_dict['func_line_dict'][k['file_name']] = value
                        elif key == 'file_name':
                            total_dict['file_name'].append(value)
                        elif key == 'is_py':
                            pass
                        elif key == 'max_indent':
                            if value > max_intent:
                                max_intent = value
                            total_dict['max_indent'] = max_intent
                        else:
                            total_dict[key] += value
            # 写入文件
            write_to_file('result.json', total_dict)

        else:
            with open(i, 'r', encoding='utf-8') as f:
                if f.name.strip().endswith('.py'):
                    res = command_lines_checker(f, True)
                    write_to_file('result.json', res)
                else:
                    res = command_lines_checker(f, False)
                    write_to_file('result.json', res)