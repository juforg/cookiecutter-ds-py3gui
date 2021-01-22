#!/usr/bin/env python
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#      SJ编程规范
# 命名：
#    1. 见名思意，变量的名字必须准确反映它的含义和内容
#    2. 遵循当前语言的变量命名规则
#    3. 不要对不同使用目的的变量使用同一个变量名
#    4. 同个项目不要使用不同名称表述同个东西
#    5. 函数/方法 使用动词+名词组合，其它使用名词组合
# 设计原则：
#    1. KISS原则： Keep it simple and stupid !
#    2. SOLID原则： S: 单一职责 O: 开闭原则 L: 迪米特法则 I: 接口隔离原则 D: 依赖倒置原则
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
# main module executed when run command
# python -m {{cookiecutter.repo_name}}_gui_main

import sys

# if __package__ is None and not hasattr(sys, 'frozen'):
#     # direct call of __main__.py
#     import os.path
#     path = os.path.realpath(os.path.abspath(__file__))
#     sys.path.insert(0, os.path.dirname(os.path.dirname(path)))

from {{cookiecutter.repo_name}} import {{cookiecutter.repo_name}}_gui_main

if __name__ == '__main__':
    {{cookiecutter.repo_name}}_gui_main.main()
