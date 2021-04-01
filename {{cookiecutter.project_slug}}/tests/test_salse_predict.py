# -*- coding: utf-8 -*-
# @author: songjie
# @email: songjie@shanshu.ai
# @date: 2021/03/31
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

import pytest
import pandas as pd

from {{cookiecutter.repo_name}}.models.sales_predict_model import SalesPredictModel

logger = logging.getLogger(__name__)


@pytest.fixture(scope='module')
def dump_path():
    dump_path = 'output/'
    return dump_path


@pytest.fixture(scope='module')
def feather_path(dump_path):
    feather_path = os.path.join(dump_path, 'features')
    return feather_path


@pytest.fixture(scope='module')
def model_path(dump_path):
    model_path = os.path.join(dump_path, 'models')
    return model_path


@pytest.fixture(scope='module')
def raw_path(dump_path):
    raw_path = os.path.join('data/', '0_raw')
    return raw_path


@pytest.fixture(scope='module')
def load_data(raw_path):
    print("开始装载数据")
    test = pd.read_csv('data/0_raw/sales/test.csv.gz')
    sales = pd.read_csv('data/0_raw/sales/sales_train.csv.gz', encoding='UTF-8')
    # sales = pd.read_csv('https://storage.googleapis.com/kaggle-competitions-data/kaggle-v2/8587/868304/compressed/sales_train.csv.zip?GoogleAccessId=web-data@kaggle-161607.iam.gserviceaccount.com&Expires=1617358534&Signature=Y2MaOnxnEFJEJyHGEcWo8TUoNYmCqt2e7oF%2BeCgx%2B4qcXKBIkTieoXUu5xzSOctQt39ow6zEjHx3v9%2FLrNVokl76laWDQoaTbuu8%2Bojg2QssJdGql3rYDE4xtWfLiZibevNa5fgBHFpkyaau56M5nEbqDUw%2BT8TCNZINMNA6VmAcYIO1nKz%2FBruZP3sMQiePLHFkeD80JawbwgJ4OzQ2fq0t0qXNPwNwfhJ%2FicHwqEF5L4Ll7m%2Bd3d1FMUrURGq5CIiOCcZQNZNdQ1RtBOIR0WTSC%2ByN2Y6269N1KiItBf8R8xNW8mu9PRSkZLk2SCiETuQzCg8c6EjT498K12j6Ig%3D%3D&response-content-disposition=attachment%3B+filename%3Dsales_train.csv.zip')
    shops = pd.read_csv('data/0_raw/sales/shops.csv')
    items = pd.read_csv('data/0_raw/sales/items.csv.gz', encoding='UTF-8')
    # items = pd.read_csv(
        # 'https://storage.googleapis.com/kaggle-competitions-data/kaggle-v2/8587/868304/compressed/items.csv.zip?GoogleAccessId=web-data@kaggle-161607.iam.gserviceaccount.com&Expires=1617357929&Signature=QFp3crHy5f1oihj2VTtqfgeXhBl2BvxDhWq%2BZhQrb%2BXOBFlbUY7dR9e7Qi4yLf%2FYh%2FLitHpTw1o4J4LNES6X380v9rEkKCE8uZK93qxm1r66%2BoS9Oj1rlDT%2F5ChHQi0gQpS%2BHYwZ%2FZKageqv7lfXUYqMV9%2FiaKgaaBcoRoVxP5PIbXnXE9l9nUl3CnVEnVHDZ%2BPf6lp%2FaeZV%2Fy%2BiaNYAAOQjXfs81Un8dq9GASTn6x4k%2Bx%2BcmWYct2AWpqQmZNqNVlERB1euDhkVI8Y2EMjJ6YyOlS9vvrkV%2FrkGnmaPp07nzUwbLroSP%2F2Z1LmJ8bntmi0dPyngn2cgfcS4ArY5Zg%3D%3D&response-content-disposition=attachment%3B+filename%3Ditems.csv.zip')
    # items.to_csv(os.path.join(raw_path, 'items.csv.gz'), compression='gzip', index=False)
    item_cats = pd.read_csv('data/0_raw/sales/item_categories.csv', encoding='UTF-8')
    print(len(test))
    print(len(sales))
    print(len(shops))
    print(len(items))
    print(len(item_cats))
    print(items.head())
    print("完成装载数据")
    return sales, shops, items, item_cats


def test_lgbm_sp(load_data, dump_path, feather_path, model_path):
    sp_model = SalesPredictModel()
    sp_model.init_data(load_data[0], load_data[1], load_data[2], load_data[3])
    sp_model.build_features()
    sp_model.dump_feature(feather_path)
    sp_model.load_features(feather_path)
    sp_model.start_trainning()
    sp_model.save_model(model_path)
    sp_model.load_model(model_path)
    result_df = sp_model.predict()
    sp_model.dump_result(dump_path)


def test_lgbm_sp_build_feature(load_data, dump_path, feather_path, model_path):
    sp_model = SalesPredictModel()
    sp_model.init_data(load_data[0], load_data[1], load_data[2], load_data[3])
    sp_model.build_features()
    sp_model.dump_feature(feather_path)


def test_lgbm_sp_train(load_data, feather_path, model_path):
    sp_model = SalesPredictModel()
    sp_model.load_features(feather_path)
    sp_model.start_trainning()
    sp_model.save_model(model_path)


def test_lgbm_sp_predict(feather_path, dump_path, model_path):
    sp_model = SalesPredictModel()
    sp_model.load_features(feather_path)
    sp_model.load_model(model_path)
    target_df = pd.read_csv('data/0_raw/sales/test.csv.gz')
    result_df = sp_model.predict(target_df)
    sp_model.dump_result(dump_path)
