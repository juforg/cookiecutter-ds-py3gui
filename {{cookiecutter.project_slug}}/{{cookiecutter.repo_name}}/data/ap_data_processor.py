# -*- coding: utf-8 -*-
# @author: songjie
# @date: 2021/03/22
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
from pandas import DataFrame

SOURCE_TP_ONE = 1
SOURCE_TP_TWO = 2


def process_raw_data(df: DataFrame, source_type: int = SOURCE_TP_ONE):
    p_fun = process_fun.get(source_type)
    if p_fun:
        return p_fun(df)
    else:
        raise Exception('未知数据源类型')


def process_raw_data_1(df: DataFrame):
    return df.iloc[:, 1:].to_numpy()


def process_raw_data_2(df: DataFrame):
    return df.iloc[:, 1:].to_numpy()


process_fun = {SOURCE_TP_ONE: process_raw_data_1, SOURCE_TP_TWO: process_raw_data_2}



