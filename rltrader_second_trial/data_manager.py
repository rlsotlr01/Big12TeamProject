import pandas as pd
import numpy as np
import settings
from sklearn.preprocessing import MinMaxScaler

# 전처리 빼곤 다 완료.
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
COLUMNS_TRAINING_DATA_V3 = [
    # 여긴 T 데이터

    # 여기부턴 F 데이터
     'roe', 'roa', 'eps', 'bps'
    , 'sales', 'margin', 'net_margin'
    , 'dps', 'debt_ratio', 'run_money'
    , 'invest_money', 'financial_money'
    # 여기서부턴 G 데이터
    , 'dollar', 'euro', 'jap'
    , 'dollaridx', 'cny', 'gold'
    , 'wti', 'nasdaq', 'dowjones'
    , 'eurostock', 'nikkei', 'hangsen'
    , 'usa2', 'usa5', 'usa10','usa30'
]


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


def preprocess_v3(data, ver='v3'):
    # (코드수정요망)
    scaler = MinMaxScaler()
    # COLUMNS_CHART_DATA = ['date', 'open', 'high', 'low', 'close', 'volume']
    # COLUMNS_TRAINING_DATA_V3 = [
    #     # 여긴 T 데이터
    #     # 여기부턴 F 데이터
    #     'roe', 'roa', 'eps', 'bps'
    #     , 'sales', 'margin', 'net_margin'
    #     , 'dps', 'debt_ratio', 'run_money'
    #     , 'invest_money', 'financial_money'
    #     # 여기서부턴 G 데이터
    #     , 'dollar', 'euro', 'jap'
    #     , 'dollaridx', 'cny', 'gold'
    #     , 'wti', 'nasdaq', 'dowjones'
    #     , 'eurostock', 'nikkei', 'hangsen'
    #     , 'usa2', 'usa5', 'usa10', 'usa30'
    # ]
    # for chart_col in COLUMNS_CHART_DATA:
    #     data[chart_col] = scaler.fit_transform(data[chart_col])
    # for col in COLUMNS_TRAINING_DATA_V3:
    #     data[col] = scaler.fit_transform(data[col])
    # 모든 컬럼에 대한 값들을 minmaxscaler 로 스케일링을 한다.
    return data


def load_data(fpath, date_from, date_to, ver='v2'):
    header = None if ver == 'v1' else 0
    if ver != 'v3':
        data = pd.read_csv(fpath, thousands=',', header=header,
            converters={'date': lambda x: str(x)})
    else:
        fpath1 = fpath.replace('.csv', 't.csv')
        fpath2 = fpath.replace('.csv', 'f.csv')
        fpath3 = settings.BASE_DIR+'/data/v3/global.csv'
        data1 = pd.read_csv(fpath1, thousands=',', header=header,
                            converters={'date': lambda x: str(x)})
        data2 = pd.read_csv(fpath2, thousands=',', header=header,
                            converters={'date': lambda x: str(x)})
        data3 = pd.read_csv(fpath3, thousands=',', header=header,
                            converters={'date': lambda x: str(x)})
        data = pd.merge(data1, data2, how='left')
        data = pd.merge(data, data3, how='left')

    if ver == 'v1':
        data.columns = ['date', 'open', 'high', 'low', 'close', 'volume']

    # 날짜 오름차순 정렬
    data = data.sort_values(by='date').reset_index()

    # 데이터 전처리
    if ver != 'v3':
        data = preprocess(data)
    else:
        data = preprocess_v3(data)
        # 버전이 v3일 경우 v3을 위한 전처리 과정을 밟는다.(코드수정요망)
    # 기간 필터링
    data['date'] = data['date'].str.replace('-', '')
    data = data[(data['date'] >= date_from) & (data['date'] <= date_to)]
    data = data.dropna()

    # 차트 데이터 분리
    chart_data = data[COLUMNS_CHART_DATA]

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
    elif ver == 'v3':
        training_data = data[COLUMNS_TRAINING_DATA_V3]
        # v3는 어떻게 전처리할 것인가? (코드수정요망)
        # 근데 tanh 를 하는건 아닌거 같은데...
        # 여기다 전처리 하지 말고, 앞의 코드에서 전처리 시키기.
        # 문자열 아닌 컬럼 다 불러와서 minmaxxcaler 해주기.
    else:
        raise Exception('Invalid version.')
    
    return chart_data, training_data
