import pandas as pd
import numpy as np


COLUMNS_CHART_DATA = ['date', 'open', 'high', 'low', 'close', 'volume']

COLUMNS_TRAINING_DATA_V1 = [
    'open_lastclose_ratio', 'high_close_ratio', 'low_close_ratio',
    'close_lastclose_ratio', 'volume_lastvolume_ratio',
    'close_ma5_ratio', 'volume_ma5_ratio',
    'close_ma10_ratio', 'volume_ma10_ratio',
    'close_ma20_ratio', 'volume_ma20_ratio',
    'close_ma60_ratio', 'volume_ma60_ratio',
    'close_ma120_ratio', 'volume_ma120_ratio',
]

COLUMNS_TRAINING_DATA_V1_RICH = [
    'open_lastclose_ratio', 'high_close_ratio', 'low_close_ratio',
    'close_lastclose_ratio', 'volume_lastvolume_ratio',
    'close_ma5_ratio', 'volume_ma5_ratio',
    'close_ma10_ratio', 'volume_ma10_ratio',
    'close_ma20_ratio', 'volume_ma20_ratio',
    'close_ma60_ratio', 'volume_ma60_ratio',
    'close_ma120_ratio', 'volume_ma120_ratio',
    'inst_lastinst_ratio', 'frgn_lastfrgn_ratio',
    'inst_ma5_ratio', 'frgn_ma5_ratio',
    'inst_ma10_ratio', 'frgn_ma10_ratio',
    'inst_ma20_ratio', 'frgn_ma20_ratio',
    'inst_ma60_ratio', 'frgn_ma60_ratio',
    'inst_ma120_ratio', 'frgn_ma120_ratio',
]

COLUMNS_TRAINING_DATA_V2 = [
    'per', 'pbr', 'roe',
    'open_lastclose_ratio', 'high_close_ratio', 'low_close_ratio',
    'close_lastclose_ratio', 'volume_lastvolume_ratio',
    'close_ma5_ratio', 'volume_ma5_ratio',
    'close_ma10_ratio', 'volume_ma10_ratio',
    'close_ma20_ratio', 'volume_ma20_ratio',
    'close_ma60_ratio', 'volume_ma60_ratio',
    'close_ma120_ratio', 'volume_ma120_ratio',
    'market_kospi_ma5_ratio', 'market_kospi_ma20_ratio', 
    'market_kospi_ma60_ratio', 'market_kospi_ma120_ratio', 
    'bond_k3y_ma5_ratio', 'bond_k3y_ma20_ratio', 
    'bond_k3y_ma60_ratio', 'bond_k3y_ma120_ratio'
]
COLUMNS_TRAINING_DATA_V3T = [
    # V3T의 컬럼들
] # (코드수정) 여기 코드 넣어줘야 함.
COLUMNS_TRAINING_DATA_V3F = [
    'roe' ,'roa' ,'eps' ,'bps'
    , 'sales', 'margin', 'net_margin'
    , 'dps', 'debt_ratio', 'run_money'
    , 'invest_money', 'financial_money'
]
# (코드수정) 여기 코드 넣어줘야 함.
COLUMNS_TRAINING_DATA_V3G = [
    # V3G의 컬럼들
] # (코드수정) 여기 코드 넣어줘야 함.

def preprocess(data, ver='v1'):
    windows = [5, 10, 20, 60, 120]
    for window in windows:
        data['close_ma{}'.format(window)] = \
            data['close'].rolling(window).mean()
        data['volume_ma{}'.format(window)] = \
            data['volume'].rolling(window).mean()
        data['close_ma%d_ratio' % window] = \
            (data['close'] - data['close_ma%d' % window]) \
            / data['close_ma%d' % window]
        data['volume_ma%d_ratio' % window] = \
            (data['volume'] - data['volume_ma%d' % window]) \
            / data['volume_ma%d' % window]

        if ver == 'v1.rich':
            data['inst_ma{}'.format(window)] = \
                data['close'].rolling(window).mean()
            data['frgn_ma{}'.format(window)] = \
                data['volume'].rolling(window).mean()
            data['inst_ma%d_ratio' % window] = \
                (data['close'] - data['inst_ma%d' % window]) \
                / data['inst_ma%d' % window]
            data['frgn_ma%d_ratio' % window] = \
                (data['volume'] - data['frgn_ma%d' % window]) \
                / data['frgn_ma%d' % window]

        # v3 버전 rolling 처리해줘야 함.
        # 과거랑 지금이랑 비슷하게 바꿔줌.

        # 데이터 전처리
        #           -> 각각의 SS / MMscaler
    data['open_lastclose_ratio'] = np.zeros(len(data))
    data.loc[1:, 'open_lastclose_ratio'] = \
        (data['open'][1:].values - data['close'][:-1].values) \
        / data['close'][:-1].values
    data['high_close_ratio'] = \
        (data['high'].values - data['close'].values) \
        / data['close'].values
    data['low_close_ratio'] = \
        (data['low'].values - data['close'].values) \
        / data['close'].values
    data['close_lastclose_ratio'] = np.zeros(len(data))
    data.loc[1:, 'close_lastclose_ratio'] = \
        (data['close'][1:].values - data['close'][:-1].values) \
        / data['close'][:-1].values
    data['volume_lastvolume_ratio'] = np.zeros(len(data))
    data.loc[1:, 'volume_lastvolume_ratio'] = \
        (data['volume'][1:].values - data['volume'][:-1].values) \
        / data['volume'][:-1] \
            .replace(to_replace=0, method='ffill') \
            .replace(to_replace=0, method='bfill').values

    if ver == 'v1.rich':
        data['inst_lastinst_ratio'] = np.zeros(len(data))
        data.loc[1:, 'inst_lastinst_ratio'] = \
            (data['inst'][1:].values - data['inst'][:-1].values) \
            / data['inst'][:-1] \
                .replace(to_replace=0, method='ffill') \
                .replace(to_replace=0, method='bfill').values
        data['frgn_lastfrgn_ratio'] = np.zeros(len(data))
        data.loc[1:, 'frgn_lastfrgn_ratio'] = \
            (data['frgn'][1:].values - data['frgn'][:-1].values) \
            / data['frgn'][:-1] \
                .replace(to_replace=0, method='ffill') \
                .replace(to_replace=0, method='bfill').values

    return data


def preprocess(data, ver='v3'):
    # v3 버전용 전처리 함수.
    windows = [5, 10, 20, 60, 120]
    # 어떻게 전처리 할 지는 나중에 상의해서 해보기.
    # (코드수정)
    return data


def load_data(fpath, date_from, date_to, ver='v2'):
    header = None if ver == 'v1' else 0
    if ver =='v1' or ver == 'v2':
        data = pd.read_csv(fpath, thousands=',', header=header,
            converters={'date': lambda x: str(x)})
    # 버전 3 용도로는 pd.read_csv 를 3번. f,g,t
    else:
        fpath1 = fpath.replace('.csv','t.csv')
        fpath2 = fpath.replace('.csv','f.csv')
        fpath3 = fpath.replace('.csv','g.csv')
        data1 = pd.read_csv(fpath1, thousands=',', header=header,
                           converters={'date': lambda x: str(x)})
        data2 = pd.read_csv(fpath2, thousands=',', header=header,
                            converters={'date': lambda x: str(x)})
        data3 = pd.read_csv(fpath3, thousands=',', header=header,
                            converters={'date': lambda x: str(x)})
        # data1, data2, data3 pd.concat(axis=1)
        # 해서 한데이터로 합쳐야되네.
        data = [data1, data2, data3]

    if ver == 'v1':
        data.columns = ['date', 'open', 'high', 'low', 'close', 'volume']

    # 날짜 오름차순 정렬
    if ver == 'v1' or ver=='v2':
        data = data.sort_values(by='date').reset_index()
    else: # v3 일 경우 data 가 리스트이기 때문에 셋 다 날짜별로 정렬해준다.
        data = [dat.sort_values(by='date').reset_index() for dat in data]



    # 데이터 전처리 -> v3 버전 따로.
    data = preprocess(data)
    
    # 기간 필터링
    data['date'] = data['date'].str.replace('-', '')
    data = data[(data['date'] >= date_from) & (data['date'] <= date_to)]
    data = data.dropna()

    # 차트 데이터 분리
    if ver != 'v3':
        chart_data = data[COLUMNS_CHART_DATA]
    else: # 'v3' 버전일 경우
        chart_data1 = data[0][COLUMNS_CHART_DATA]
        chart_data2 = data[1][COLUMNS_CHART_DATA]
        chart_data3 = data[2][COLUMNS_CHART_DATA]

    # 학습 데이터 분리
    training_data = None
    if ver == 'v1':
        training_data = data[COLUMNS_TRAINING_DATA_V1]
    elif ver == 'v1.rich':
        training_data = data[COLUMNS_TRAINING_DATA_V1_RICH]
    elif ver == 'v2':
        data.loc[:, ['per', 'pbr', 'roe']] = \
            data[['per', 'pbr', 'roe']].apply(lambda x: x / 100)
        training_data = data[COLUMNS_TRAINING_DATA_V2]
        training_data = training_data.apply(np.tanh)
    # 여기 v3 넣어주고,
    # 필요한 데이터들 나눠주기.
    elif ver == 'v3':
        # 전처리 코드 넣고, -> preprocess preprocess(data)
        # chart_data1, ... 이건 어떻게 넣어줄까?
        # 데이터 3개 컬럼 training_data 각각 넣어주고,
        # return (chart_data1, training_data1, chart_data2, training_data2, chart_data3, training_data3)
        training_data1T = data[0][COLUMNS_TRAINING_DATA_V3T] # 리스트 형식이면 이렇게 넣어줘야 할까?
        training_data2F = data[1][COLUMNS_TRAINING_DATA_V3F]
        training_data3G = data[2][COLUMNS_TRAINING_DATA_V3G]
        list_chart_data = [chart_data1, chart_data2, chart_data3]
        list_training_data = [training_data1T, training_data2F, training_data3G]
        return (list_chart_data, list_training_data)
        # list_chart_data 와 list_training_data 를 돌려준다.
#        data.loc[:, ['per', 'pbr', 'roe']] = \
#            data[['per', 'pbr', 'roe']].apply(lambda x: x / 100) 이런 방식으로 scaling 해주면 될 것 같은데?
    else:
        raise Exception('Invalid version.')
    
    return chart_data, training_data
