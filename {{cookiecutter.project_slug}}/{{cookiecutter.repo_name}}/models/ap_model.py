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
import logging
from mip import Model, xsum, BINARY, MINIMIZE, CBC, minimize, OptimizationStatus
from typing import List

logger = logging.getLogger(__name__)


class AP:
    """
    指派问题求解。

    """
    ap_model = None  # 模型
    dec_vars = None  # decision variable 决策变量
    is_init = False  # 是否初始化
    opt_status = None  # 求解状态

    def __init__(self, profit_matrix: List[int]):
        """
        初始化
        """
        self.profit_matrix = profit_matrix

    def init_model(self):
        # 1. 选择求解器初始化
        self.ap_model = Model(sense=MINIMIZE, solver_name=CBC)
        # 2. 定义决策变量
        self.dec_vars = [[self.ap_model.add_var(var_type=BINARY) for i in range(len(self.profit_matrix))] for j in range(len(self.profit_matrix))]
        # 3. 定义目标函数
        self.ap_model.objective = minimize(xsum(self.dec_vars[i][j] * self.profit_matrix[i][j] for i in range(len(self.profit_matrix)) for j in range(len(self.profit_matrix))))
        # 4. 定义约束条件
        for i in range(len(self.profit_matrix)):  # 每行只能有一个1
            self.ap_model.add_constr(xsum(self.dec_vars[i][j] for j in range(len(self.profit_matrix))) == 1)
        for j in range(len(self.profit_matrix)):  # 每列只能有一个1
            self.ap_model.add_constr(xsum(self.dec_vars[i][j] for i in range(len(self.profit_matrix))) == 1)
        self.is_init = True

    def solve(self, max_seconds: int = 10):
        """
        设定约束时间开始求解
        :param max_seconds:
        :return:
        """
        if not self.is_init:
            self.init_model()
        self.opt_status = self.ap_model.optimize(max_seconds=max_seconds)
        return self.opt_status

    def get_optimum_val(self):
        """
        获取最优解值
        :return:
        """
        if self.opt_status and self.opt_status == OptimizationStatus.OPTIMAL:
            return self.ap_model.objective_value
        else:
            raise Exception('未求得解')

    def get_optimum_sol(self):
        """
        获取最优解变量
        :return:
        """
        if self.opt_status and self.opt_status == OptimizationStatus.OPTIMAL:
            return self.dec_vars
        else:
            raise Exception('未求得解')
