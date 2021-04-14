# -*- coding: utf-8 -*-
# @author: songjie
# @email: songjie@shanshu.ai
# @date: 2021/03/24
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
import os

import lightgbm as lgb
import pandas as pd
from enum import Enum
import numpy as np

from {{cookiecutter.repo_name}}.features.sales_features import build_shop_features, build_item_features, build_date_features, build_interaction_features, build_lag_features, \
    build_avg_shop_item_price_features, build_target_enc_features, build_extra_interaction_features, lag_feature_adv, build_feature_matrix

logger = logging.getLogger(__name__)

LGB_PARAMS = {
    'objective': 'mse',
    'metric': 'rmse',
    'num_leaves': 2 ** 7 - 1,
    'learning_rate': 0.005,
    'feature_fraction': 0.75,
    'bagging_fraction': 0.75,
    'bagging_freq': 5,
    'seed': 1,
    'verbose': 0  # 控制台是否输出
}


class ItemKey(Enum):
    ITEM_ID = 'item_id'
    ITEM_CATEGORY_COMMON = 'item_category_common'
    ITEM_CATEGORY_CODE = 'item_category_code'


class ShopKey(Enum):
    SHOP_ID = 'shop_id'
    CITY_CODE = 'city_code'
    CITY_COORD_1 = 'city_coord_1'
    CITY_COORD_2 = 'city_coord_2'
    COUNTRY_PART = 'country_part'


AVG_ITEM_PRICE_COLS = ['item_id', 'date_block_num']
AVG_SHOP_ITEM_PRICE_COLS = ['shop_id', 'item_id', 'date_block_num']
CATEGORICAL_FEATURE_NAMES = [
    'country_part',
    'item_category_common',
    'item_category_code',
    'city_code',
]


# todo 添加计算耗时 修饰器
# todo 维度转换 数据不需要到日


class SalesPredictModel:

    sales_log_df: pd.DataFrame = None  # 销售记录
    train_df: pd.DataFrame = None  # 训练集
    shops_df: pd.DataFrame = None  # 商店信息
    items_df: pd.DataFrame = None  # 商品信息
    item_categories_df: pd.DataFrame = None  # 商品分类
    test_df: pd.DataFrame = None  # 测试集 非必须
    train_label = []
    sp_gbm_model = None
    date_block_item_avg_price_df: pd.DataFrame = None  # 每个阶段 商品总的销售均价
    date_block_item_shop_avg_price_df: pd.DataFrame = None  # 每个阶段 商品在所有门店各自的销售均价
    feature_name = ['shop_id', 'item_id', 'date_block_num', 'city_code', 'city_coord_1', 'city_coord_2', 'country_part', 'item_category_common', 'item_category_code', 'weeknd_count', 'days_in_month', 'item_first_interaction', 'shop_item_sold_before', 'item_cnt_month_lag_1_adv', 'item_cnt_month_lag_2_adv', 'item_cnt_month_lag_3_adv']  # 特征列表
    feature_matrix_df = None  # 特征矩阵
    result_df = None  # 预测结果
    """
    销售预测模型
    """

    def __init__(self):
        """
        初始化
        """

    def init_data(self, sales_log: pd.DataFrame, shops: pd.DataFrame, items: pd.DataFrame, item_categories: pd.DataFrame):
        """
        初始化数据
        :return:
        """
        self.sales_log_df = sales_log
        self.train_df = sales_log
        self.shops_df = shops
        self.items_df = items
        self.item_categories_df = item_categories
        self.date_block_item_avg_price_df = self.sales_log_df.groupby(AVG_ITEM_PRICE_COLS)['item_price'].mean().reset_index().rename(columns={"item_price": "avg_item_price"},
                                                                                                                                     errors="raise")
        self.date_block_item_shop_avg_price_df = self.sales_log_df.groupby(AVG_SHOP_ITEM_PRICE_COLS)['item_price'].mean().reset_index().rename(
            columns={"item_price": "avg_shop_price"}, errors="raise")
        # 去除 异常值 todo 不适合在模型中做，应放在前置 etl中
        self.train_df = self.sales_log_df[(self.sales_log_df.item_price < 100000) & (self.sales_log_df.item_price > 0)]
        self.train_df = self.train_df[self.sales_log_df.item_cnt_day < 1001]

    def build_features(self):
        """
        构建特征
        :return:
        """
        logger.info("开始构建特征")
        self.feature_matrix_df = build_feature_matrix(self.train_df)
        logger.info(f"特征矩阵占用内存:{self.feature_matrix_df.memory_usage().sum() / 1024 ** 2}Mb")
        # 构建门店特征
        self.shops_df = build_shop_features(self.shops_df)
        self.shops_df = self.shops_df[[e.value for e in ShopKey]]
        self.feature_matrix_df = pd.merge(self.feature_matrix_df, self.shops_df, on=['shop_id'], how='left')
        # 构建商品特征
        self.items_df = build_item_features(self.items_df, self.item_categories_df)
        self.items_df = self.items_df[[e.value for e in ItemKey]]
        self.feature_matrix_df = pd.merge(self.feature_matrix_df, self.items_df, on=['item_id'], how='left')
        logger.info(f"特征矩阵占用内存:{self.feature_matrix_df.memory_usage().sum() / 1024 ** 2}Mb")
        # 构建日期特征
        self.feature_matrix_df = build_date_features(self.feature_matrix_df)
        # 构建商品门店间相互作用特征
        self.feature_matrix_df, _, _ = build_interaction_features(self.feature_matrix_df)
        # Add sales lags for last 3 months
        self.feature_matrix_df = build_lag_features(self.feature_matrix_df, [1, 2, 3], 'item_cnt_month')
        logger.info(f"特征矩阵占用内存:{self.feature_matrix_df.memory_usage().sum() / 1024 ** 2}Mb")
        self.feature_matrix_df = build_avg_shop_item_price_features(self.feature_matrix_df, self.date_block_item_shop_avg_price_df, self.date_block_item_avg_price_df)
        self.feature_matrix_df = build_target_enc_features(self.feature_matrix_df)
        self.feature_matrix_df = build_extra_interaction_features(self.feature_matrix_df)
        self.feature_matrix_df = lag_feature_adv(self.feature_matrix_df, [1, 2, 3], 'item_cnt_month')
        logger.info(f"特征矩阵占用内存:{self.feature_matrix_df.memory_usage().sum() / 1024 ** 2}Mb")
        # Remove data for the first three months
        self.feature_matrix_df.fillna(0, inplace=True)
        self.feature_matrix_df = self.feature_matrix_df[(self.feature_matrix_df['date_block_num'] > 2)]
        self.feature_matrix_df.drop(['ID'], axis=1, inplace=True, errors='ignore')
        logger.info(f"特征矩阵占用内存:{self.feature_matrix_df.memory_usage().sum() / 1024 ** 2}Mb")
        logger.info("完成构建特征")

    def load_features(self, dump_path, replace=True):
        """
        加载已有特征矩阵
        :return:
        """
        if self.feature_matrix_df is None or self.feature_matrix_df.empty or replace:
            self.feature_matrix_df = pd.read_pickle(os.path.join(dump_path, 'sales_feature_matrix.pkl'))
            # self.feature_matrix_df.info()
        else:
            # todo 合并特征矩阵
            logger.info('start merge features')

    def dump_feature(self, dump_path):
        """
        存储构建好的特征矩阵
        :return:
        """
        self.feature_matrix_df.to_pickle(os.path.join(dump_path, 'sales_feature_matrix.pkl'))

    def split_datasets(self):
        """
        数据集拆分, 不建议在 模型内部拆分, 方法用于测试
        train , test
        :return:
        """
        logger.info("开始拆分数据集")

    def start_trainning(self):
        """
        开始训练
        :return:
        """

        logger.info("开始训练")
        x_train = self.feature_matrix_df[self.feature_matrix_df.date_block_num < 33].drop(['item_cnt_month'], axis=1)
        y_train = self.feature_matrix_df[self.feature_matrix_df.date_block_num < 33]['item_cnt_month']
        x_valid = self.feature_matrix_df[self.feature_matrix_df.date_block_num == 33].drop(['item_cnt_month'], axis=1)
        y_valid = self.feature_matrix_df[self.feature_matrix_df.date_block_num == 33]['item_cnt_month']
        self.feature_name = x_train.columns.tolist()
        lgb_train = lgb.Dataset(x_train[self.feature_name], y_train)
        lgb_eval = lgb.Dataset(x_valid[self.feature_name], y_valid, reference=lgb_train)
        evals_result = {}
        self.sp_gbm_model = lgb.train(
            LGB_PARAMS,
            lgb_train,
            num_boost_round=3000,
            valid_sets=(lgb_train, lgb_eval),
            feature_name=self.feature_name,
            categorical_feature=CATEGORICAL_FEATURE_NAMES,
            verbose_eval=5,
            evals_result=evals_result,
            early_stopping_rounds=100)

        logger.info("训练完成")

    def save_model(self, dump_path):
        """
        保存训练好的模型
        :return:
        """
        # todo 压缩模型
        self.sp_gbm_model.save_model(os.path.join(dump_path, 'sp_gbm_model.txt'))

    def load_model(self, dump_path):
        """
        加载训练好的模型
        :return:
        """
        # todo 解压模型
        self.sp_gbm_model = lgb.Booster(model_file=os.path.join(dump_path, 'sp_gbm_model.txt'))

    def predict(self, target_df):
        """
        开始预测
        :param target_df:
        :return:
        """
        logger.info("开始预测")
        # add target
        target_df['date_block_num'] = 34
        target_df['date_block_num'] = target_df['date_block_num'].astype(np.int8)
        target_df['shop_id'] = target_df['shop_id'].astype(np.int8)
        target_df['item_id'] = target_df['item_id'].astype(np.int16)
        target_matrix_df = pd.concat([self.feature_matrix_df, target_df], ignore_index=True, sort=False, keys=AVG_SHOP_ITEM_PRICE_COLS)
        target_matrix_df.fillna(0, inplace=True)

        feature_name = self.feature_matrix_df[self.feature_matrix_df.date_block_num < 33].drop(['item_cnt_month'], axis=1).columns.tolist()
        x_test = target_matrix_df[target_matrix_df.date_block_num == 34].drop(['item_cnt_month'], axis=1)
        y_test = self.sp_gbm_model.predict(x_test[feature_name]).clip(0, 20)

        self.result_df = pd.DataFrame({
            "ID": target_df.index,
            "item_cnt_month": y_test
        })
        logger.info("预测完成")
        return self.result_df

    def dump_result(self, dump_path):
        self.result_df.to_csv(os.path.join(dump_path, 'predict_result.csv'), index=False)
