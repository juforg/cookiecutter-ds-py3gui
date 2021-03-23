# -*- coding: utf-8 -*-
# @author: songjie
# @date: 2021/03/19
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

import pytest
import pandas as pd
from {{cookiecutter.repo_name}}.data.ap_data_processor import process_raw_data
from {{cookiecutter.repo_name}}.models.ap_model import AP


def test_mip_or_ap():
    raw_df = pd.read_csv('data/0_raw/profit_matrix.csv.zip', header=0)
    profit_matrix = process_raw_data(raw_df)
    ap_model = AP(profit_matrix)
    ap_model.init_model()
    opt_status = ap_model.solve()
    print(ap_model.get_optimum_val())
    optimum_sols = ap_model.get_optimum_sol()
    opt_vals = []
    for idx, xi in enumerate(optimum_sols):
        x_list = [xij.x for xij in xi]
        x_list.insert(0, raw_df.iloc[idx, 0])
        opt_vals.append(x_list)
    result_df = pd.DataFrame(opt_vals, columns=raw_df.columns)
    result_df.to_csv('output/result.csv.gz', compression='gzip', index=False)
