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
import calendar
from itertools import product

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder


def build_shop_features(shops_df: pd.DataFrame):
    """
    构建商店特征
    :param shops_df:
    :return:
    """
    shops_df['city'] = shops_df['shop_name'].apply(lambda x: x.split()[0].lower())
    shops_df.loc[shops_df.city == '!якутск', 'city'] = 'якутск'
    shops_df['city_code'] = LabelEncoder().fit_transform(shops_df['city'])

    coords = dict()
    coords['якутск'] = (62.028098, 129.732555, 4)
    coords['адыгея'] = (44.609764, 40.100516, 3)
    coords['балашиха'] = (55.8094500, 37.9580600, 1)
    coords['волжский'] = (53.4305800, 50.1190000, 3)
    coords['вологда'] = (59.2239000, 39.8839800, 2)
    coords['воронеж'] = (51.6720400, 39.1843000, 3)
    coords['выездная'] = (0, 0, 0)
    coords['жуковский'] = (55.5952800, 38.1202800, 1)
    coords['интернет-магазин'] = (0, 0, 0)
    coords['казань'] = (55.7887400, 49.1221400, 4)
    coords['калуга'] = (54.5293000, 36.2754200, 4)
    coords['коломна'] = (55.0794400, 38.7783300, 4)
    coords['красноярск'] = (56.0183900, 92.8671700, 4)
    coords['курск'] = (51.7373300, 36.1873500, 3)
    coords['москва'] = (55.7522200, 37.6155600, 1)
    coords['мытищи'] = (55.9116300, 37.7307600, 1)
    coords['н.новгород'] = (56.3286700, 44.0020500, 4)
    coords['новосибирск'] = (55.0415000, 82.9346000, 4)
    coords['омск'] = (54.9924400, 73.3685900, 4)
    coords['ростовнадону'] = (47.2313500, 39.7232800, 3)
    coords['спб'] = (59.9386300, 30.3141300, 2)
    coords['самара'] = (53.2000700, 50.1500000, 4)
    coords['сергиев'] = (56.3000000, 38.1333300, 4)
    coords['сургут'] = (61.2500000, 73.4166700, 4)
    coords['томск'] = (56.4977100, 84.9743700, 4)
    coords['тюмень'] = (57.1522200, 65.5272200, 4)
    coords['уфа'] = (54.7430600, 55.9677900, 4)
    coords['химки'] = (55.8970400, 37.4296900, 1)
    coords['цифровой'] = (0, 0, 0)
    coords['чехов'] = (55.1477000, 37.4772800, 4)
    coords['ярославль'] = (57.6298700, 39.8736800, 2)

    shops_df['city_coord_1'] = shops_df['city'].apply(lambda x: coords[x][0])
    shops_df['city_coord_2'] = shops_df['city'].apply(lambda x: coords[x][1])
    shops_df['country_part'] = shops_df['city'].apply(lambda x: coords[x][2])
    shops_df = shops_df[['shop_id', 'city_code', 'city_coord_1', 'city_coord_2', 'country_part']]
    return shops_df


def build_item_features(items_df: pd.DataFrame, item_cats_df: pd.DataFrame):
    """
    构建商品特征
    :param items_df:
    :param item_cats_df:
    :return:
    """
    map_dict = {
        'Чистые носители (штучные)': 'Чистые носители',
        'Чистые носители (шпиль)': 'Чистые носители',
        'PC ': 'Аксессуары',
        'Служебные': 'Служебные '
    }

    items_df = pd.merge(items_df, item_cats_df, on='item_category_id')

    items_df['item_category'] = items_df['item_category_name'].apply(lambda x: x.split('-')[0])
    items_df['item_category'] = items_df['item_category'].apply(lambda x: map_dict[x] if x in map_dict.keys() else x)
    items_df['item_category_common'] = LabelEncoder().fit_transform(items_df['item_category'])
    items_df['item_category_code'] = LabelEncoder().fit_transform(items_df['item_category_name'])
    items_df = items_df[['item_id', 'item_category_common', 'item_category_code']]
    return items_df


def count_days(date_block_num):
    """
    返回当前日的特征， 下面逻辑有问题 根据实际修改
    :param date_block_num:
    :return:
    """
    year = 2013 + date_block_num // 12
    month = 1 + date_block_num % 12
    weeknd_count = len([1 for i in calendar.monthcalendar(year, month) if i[6] != 0])
    days_in_month = calendar.monthrange(year, month)[1]
    return weeknd_count, days_in_month, month


def build_feature_matrix(train_df: pd.DataFrame):
    index_cols = ['shop_id', 'item_id', 'date_block_num']

    feature_matrix_df = []
    for block_num in train_df['date_block_num'].unique():
        cur_shops = train_df.loc[train_df['date_block_num'] == block_num, 'shop_id'].unique()
        cur_items = train_df.loc[train_df['date_block_num'] == block_num, 'item_id'].unique()
        feature_matrix_df.append(np.array(list(product(*[cur_shops, cur_items, [block_num]])), dtype='int32'))

    feature_matrix_df = pd.DataFrame(np.vstack(feature_matrix_df), columns=index_cols, dtype=np.int32)

    # Add month sales
    group = train_df.groupby(['date_block_num', 'shop_id', 'item_id']).agg({'item_cnt_day': ['sum']})
    group.columns = ['item_cnt_month']
    group.reset_index(inplace=True)

    feature_matrix_df = pd.merge(feature_matrix_df, group, on=index_cols, how='left')
    feature_matrix_df['item_cnt_month'] = (feature_matrix_df['item_cnt_month']
                                           .fillna(0)
                                           .clip(0, 20)
                                           .astype(np.float16))
    return feature_matrix_df


def build_date_features(feature_matrix_df: pd.DataFrame):
    """
    构建销售日期特征
    :param feature_matrix_df:
    :return:
    """
    map_dict = {i: count_days(i) for i in range(35)}

    feature_matrix_df['weeknd_count'] = feature_matrix_df['date_block_num'].apply(lambda x: map_dict[x][0])
    feature_matrix_df['days_in_month'] = feature_matrix_df['date_block_num'].apply(lambda x: map_dict[x][1])
    return feature_matrix_df


def build_interaction_features(feature_matrix_df: pd.DataFrame):
    """
    构建商品门店间相互作用特征
    :param feature_matrix_df:
    :return:
    """
    first_item_block_df = feature_matrix_df.groupby(['item_id'])['date_block_num'].min().reset_index()
    first_item_block_df['item_first_interaction'] = 1

    first_shop_item_buy_block_df = feature_matrix_df[feature_matrix_df['date_block_num'] > 0].groupby(['shop_id', 'item_id'])['date_block_num'].min().reset_index()
    first_shop_item_buy_block_df['first_date_block_num'] = first_shop_item_buy_block_df['date_block_num']
    feature_matrix_df = pd.merge(feature_matrix_df, first_item_block_df[['item_id', 'date_block_num', 'item_first_interaction']], on=['item_id', 'date_block_num'], how='left')
    feature_matrix_df = pd.merge(feature_matrix_df, first_shop_item_buy_block_df[['item_id', 'shop_id', 'first_date_block_num']], on=['item_id', 'shop_id'], how='left')

    feature_matrix_df['first_date_block_num'].fillna(100, inplace=True)
    feature_matrix_df['shop_item_sold_before'] = (feature_matrix_df['first_date_block_num'] < feature_matrix_df['date_block_num']).astype('int8')
    feature_matrix_df.drop(['first_date_block_num'], axis=1, inplace=True)

    feature_matrix_df['item_first_interaction'].fillna(0, inplace=True)
    feature_matrix_df['shop_item_sold_before'].fillna(0, inplace=True)

    feature_matrix_df['item_first_interaction'] = feature_matrix_df['item_first_interaction'].astype('int8')
    feature_matrix_df['shop_item_sold_before'] = feature_matrix_df['shop_item_sold_before'].astype('int8')

    return feature_matrix_df, first_item_block_df, first_shop_item_buy_block_df


def build_lag_features(feature_matrix_df: pd.DataFrame, lags, col):
    """
    构建滞后特征
    :param feature_matrix_df:
    :param lags:
    :param col:
    :return:
    """
    tmp = feature_matrix_df[['date_block_num', 'shop_id', 'item_id', col]]
    for i in lags:
        shifted = tmp.copy()
        shifted.columns = ['date_block_num', 'shop_id', 'item_id', col + '_lag_' + str(i)]
        shifted['date_block_num'] += i
        df = pd.merge(feature_matrix_df, shifted, on=['date_block_num', 'shop_id', 'item_id'], how='left')
        df[col + '_lag_' + str(i)] = df[col + '_lag_' + str(i)].astype('float16')
    return feature_matrix_df


AVG_ITEM_PRICE_COLS = ['item_id', 'date_block_num']
AVG_SHOP_ITEM_PRICE_COLS = ['shop_id', 'item_id', 'date_block_num']


def build_avg_shop_item_price_features(feature_matrix_df: pd.DataFrame, date_block_item_shop_avg_price_df, date_block_item_avg_price_df):
    feature_matrix_df = pd.merge(feature_matrix_df, date_block_item_avg_price_df, on=AVG_ITEM_PRICE_COLS, how='left')
    feature_matrix_df = pd.merge(feature_matrix_df, date_block_item_shop_avg_price_df, on=AVG_SHOP_ITEM_PRICE_COLS, how='left')
    feature_matrix_df['avg_shop_price'] = (feature_matrix_df['avg_shop_price']
                                           .fillna(0)
                                           .astype(np.float16))
    feature_matrix_df['avg_item_price'] = (feature_matrix_df['avg_item_price']
                                           .fillna(0)
                                           .astype(np.float16))
    feature_matrix_df['item_shop_price_avg'] = (feature_matrix_df['avg_shop_price'] - feature_matrix_df['avg_item_price']) / feature_matrix_df[
        'avg_item_price']
    feature_matrix_df['item_shop_price_avg'].fillna(0, inplace=True)
    feature_matrix_df = build_lag_features(feature_matrix_df, [1, 2, 3], 'item_shop_price_avg')
    feature_matrix_df.drop(['avg_shop_price', 'avg_item_price', 'item_shop_price_avg'], axis=1, inplace=True)
    return feature_matrix_df


def build_target_enc_features(feature_matrix_df: pd.DataFrame):
    item_id_target_mean = feature_matrix_df.groupby(['date_block_num', 'item_id'])['item_cnt_month'].mean().reset_index().rename(columns={"item_cnt_month": "item_target_enc"},
                                                                                                                                 errors="raise")
    feature_matrix_df = pd.merge(feature_matrix_df, item_id_target_mean, on=['date_block_num', 'item_id'], how='left')

    feature_matrix_df['item_target_enc'] = (feature_matrix_df['item_target_enc']
                                            .fillna(0)
                                            .astype(np.float16))

    feature_matrix_df = build_lag_features(feature_matrix_df, [1, 2, 3], 'item_target_enc')
    feature_matrix_df.drop(['item_target_enc'], axis=1, inplace=True)

    # Add target encoding for item/city for last 3 months
    item_id_target_mean = feature_matrix_df.groupby(['date_block_num', 'item_id', 'city_code'])['item_cnt_month'].mean().reset_index().rename(columns={
        "item_cnt_month": "item_loc_target_enc"}, errors="raise")
    feature_matrix_df = pd.merge(feature_matrix_df, item_id_target_mean, on=['date_block_num', 'item_id', 'city_code'], how='left')

    feature_matrix_df['item_loc_target_enc'] = (feature_matrix_df['item_loc_target_enc']
                                                .fillna(0)
                                                .astype(np.float16))

    feature_matrix_df = build_lag_features(feature_matrix_df, [1, 2, 3], 'item_loc_target_enc')
    feature_matrix_df.drop(['item_loc_target_enc'], axis=1, inplace=True)

    # Add target encoding for item/shop for last 3 months
    item_id_target_mean = feature_matrix_df.groupby(['date_block_num', 'item_id', 'shop_id'])['item_cnt_month'].mean().reset_index().rename(columns={
        "item_cnt_month": "item_shop_target_enc"}, errors="raise")

    feature_matrix_df = pd.merge(feature_matrix_df, item_id_target_mean, on=['date_block_num', 'item_id', 'shop_id'], how='left')

    feature_matrix_df['item_shop_target_enc'] = (feature_matrix_df['item_shop_target_enc']
                                                 .fillna(0)
                                                 .astype(np.float16))

    feature_matrix_df = build_lag_features(feature_matrix_df, [1, 2, 3], 'item_shop_target_enc')
    feature_matrix_df.drop(['item_shop_target_enc'], axis=1, inplace=True)
    return feature_matrix_df


def build_extra_interaction_features(feature_matrix_df: pd.DataFrame):
    # For new items add avg category sales for last 3 months
    item_id_target_mean = feature_matrix_df[feature_matrix_df['item_first_interaction'] == 1].groupby(['date_block_num', 'item_category_code'])[
        'item_cnt_month'].mean().reset_index().rename(columns={
        "item_cnt_month": "new_item_cat_avg"}, errors="raise")

    feature_matrix_df = pd.merge(feature_matrix_df, item_id_target_mean, on=['date_block_num', 'item_category_code'], how='left')

    feature_matrix_df['new_item_cat_avg'] = (feature_matrix_df['new_item_cat_avg']
                                             .fillna(0)
                                             .astype(np.float16))

    feature_matrix_df = build_lag_features(feature_matrix_df, [1, 2, 3], 'new_item_cat_avg')
    feature_matrix_df.drop(['new_item_cat_avg'], axis=1, inplace=True)
    # For new items add avg category sales in a separate store for last 3 months
    item_id_target_mean = feature_matrix_df[feature_matrix_df['item_first_interaction'] == 1].groupby(['date_block_num', 'item_category_code', 'shop_id'])[
        'item_cnt_month'].mean().reset_index().rename(columns={
        "item_cnt_month": "new_item_shop_cat_avg"}, errors="raise")

    feature_matrix_df = pd.merge(feature_matrix_df, item_id_target_mean, on=['date_block_num', 'item_category_code', 'shop_id'], how='left')

    feature_matrix_df['new_item_shop_cat_avg'] = (feature_matrix_df['new_item_shop_cat_avg']
                                                  .fillna(0)
                                                  .astype(np.float16))

    feature_matrix_df = build_lag_features(feature_matrix_df, [1, 2, 3], 'new_item_shop_cat_avg')
    feature_matrix_df.drop(['new_item_shop_cat_avg'], axis=1, inplace=True)
    return feature_matrix_df


def lag_feature_adv(feature_matrix_df, lags, col):
    tmp = feature_matrix_df[['date_block_num', 'shop_id', 'item_id', col]]
    for i in lags:
        shifted = tmp.copy()
        shifted.columns = ['date_block_num', 'shop_id', 'item_id', col + '_lag_' + str(i) + '_adv']
        shifted['date_block_num'] += i
        shifted['item_id'] -= 1
        feature_matrix_df = pd.merge(feature_matrix_df, shifted, on=['date_block_num', 'shop_id', 'item_id'], how='left')
        feature_matrix_df[col + '_lag_' + str(i) + '_adv'] = feature_matrix_df[col + '_lag_' + str(i) + '_adv'].astype('float16')
    return feature_matrix_df
