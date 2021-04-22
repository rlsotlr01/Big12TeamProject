import sqlite3
import pandas as pd
import os
import numpy as np

codes_list = []
csv_path = './naver_data/'
csv_files = [csv_path + '무선통신서비스.csv', csv_path + '복합기업.csv', csv_path + '전자장비와기기.csv', csv_path + '화학.csv',
             csv_path + '철강.csv'
    , csv_path + 'IT서비스.csv', csv_path + '해운사.csv', csv_path + '조선.csv', csv_path + '광고.csv', csv_path + '건설.csv'
    , csv_path + '건설.csv', csv_path + '게임엔터테인먼트.csv', csv_path + '은행.csv', csv_path + '손해보험.csv',
             csv_path + '생명보험.csv', csv_path + '증권.csv'
    , csv_path + '식품.csv', csv_path + '화장품.csv', csv_path + '백화점과일반상점.csv', csv_path + '석유와가스.csv',
             csv_path + '음료.csv'
    , csv_path + '반도체와반도체장비.csv', csv_path + '기계.csv', csv_path + '자동차.csv', csv_path + '자동차부품.csv',
             csv_path + '가정용기기와용품.csv'
    , csv_path + '방송과엔터테인먼트.csv', csv_path + '항공화물운송과물류.csv', csv_path + '통신장비.csv', csv_path + '소프트웨어.csv',
             csv_path + '섬유,의류,신발,호화품.csv'
    , csv_path + '제약.csv', csv_path + '생명과학도구및서비스.csv', csv_path + '건축자재.csv', csv_path + '생물공학.csv',
             csv_path + '가스유틸리티.csv']
# 추가할 csv 파일을 넣어준다.

for csv_file in csv_files:
    # 각각의 csv 파일을 읽으며 code 를 담는다.
    data = pd.read_csv(csv_file)
    for code in list(data['code']):
        codes_list.append(code)

# 실시간데이터는 199개까지로 제한. 200개 부턴 안됨.
# 위에는 DB에서 종목코드 가져오는 코딩. 제대로 작동함.
codes = codes_list  # 모든 종목코드를 담음.

# db 안에 있는 데이터를 csv로 만들어주는 함수. (기능 완료)
def sql_to_csv(codes):
    # code 는 A 포함하지 않고 넣어줘야 함. ex.005930 이렇게.
    # 사용할 데이터의 위치
    data_loc = './data'
    base = './merged_data'
    filepath = base+'/csvfiles'
    # code = 'A'+code
    # csvfiles 폴더가 존재하지 않으면 해당 폴더를 만든다.
    if not os.path.exists(filepath):
        os.mkdir(filepath)
    db=sqlite3.connect(data_loc+'/stock_db(day)_merge_new.db')

    for elem in codes:
        selected_data = pd.read_sql_query("SELECT * FROM {}".format(elem), db)
        # 해당 코드의 csv 파일을 저장한다.
        selected_data.to_csv(filepath+"/{}.csv".format(elem[1:]),index=False)
    return selected_data

# csv 를 불러와서 전처리 하기 위한 용도 (완료)
# - monkey 강화학습에 필요한 컬럼(day, cur_pr, high_pr, low_pr, clo_pr, for_stor만 뽑아내고,
# - 컬럼명 변경 (date, open, high, low, close, volume)
def select_cols_for_monkey(codes):

    filepath = './merged_data/csvfiles'
    result_path = './merged_data/processed_csvfiles'
    if not os.path.exists(result_path):
        os.mkdir(result_path)

    for elem in codes:
        data = pd.read_csv(filepath+"/{}.csv".format(elem[1:]))
        data = data.sort_values('day', ascending = True)
        data['day']=data['day'].astype(str)
        new_data = data[['day','cur_pr','high_pr','low_pr','clo_pr','acc_vol', 'com_buy_vol', 'for_stor']]
        bool1 = new_data['day']>='20101001'
        bool2 = new_data['day']<'20210101'

        processed_data = new_data[bool1&bool2]

        col_processed_data = processed_data.rename(columns = {'day':'date','cur_pr':'open','high_pr':'high','low_pr':'low','clo_pr':'close','acc_vol':'volume', 'com_buy_vol':'korcom', 'for_stor':'forvol'})
        col_processed_data.to_csv(result_path+"/{}.csv".format(elem[1:]),index=False)

    return col_processed_data

def cal_std(codes):
    filepath = './merged_data/processed_csvfiles'
    result_path = './merged_data/trend_csvfiles'
    if not os.path.exists(result_path):
        os.mkdir(result_path)
    for elem in codes:
        data = pd.read_csv(filepath + "/{}.csv".format(elem[1:]))
        # data['close'].fillna(value=0)

        std5 = data['close'].rolling(5).std(ddof=0) # ddof를 명시 함으로써 모표쥰편차가 아닌 표본표준편차가 계산된다.
        std10 = data['close'].rolling(10).std(ddof=0)
        std20 = data['close'].rolling(20).std(ddof=0)
        std60 = data['close'].rolling(60).std(ddof=0)
        std120 = data['close'].rolling(120).std(ddof=0)

        data['standard deviation5'] = std5
        data['standard deviation10'] = std10
        data['standard deviation20'] = std20
        data['standard deviation60'] = std60
        data['standard deviation120'] = std120

        trend_data = data
        trend_data.to_csv(result_path + "/{}t.csv".format(elem[1:]), index=False)

    return trend_data

def cal_ma(codes):
    filepath = './merged_data/trend_csvfiles'

    for elem in codes:
        data = pd.read_csv(filepath + "/{}t.csv".format(elem[1:]))

        # MA5, MA10, MA20, MA60 컬럼 추가
        ma5 = data['close'].rolling(5).mean()
        ma10 = data['close'].rolling(10).mean()
        ma20 = data['close'].rolling(20).mean()
        ma60 = data['close'].rolling(60).mean()
        ma120 = data['close'].rolling(120).mean()

        data['ma5'] = ma5
        data['ma10'] = ma10
        data['ma20'] = ma20
        data['ma60'] = ma60
        data['ma120'] = ma120

        trend_data = data
        trend_data.to_csv(filepath+"/{}t.csv".format(elem[1:]), index=False)

    return trend_data

# MACD 구하는 함수
# EMA(Exponential Moving Average) = 지수 이동 평균
# MACD = EMA(numFast) - EMA(numSlow)
# ewm() => rolling() 함수와 비슷하게 사용
def cal_MACD(codes, num_fast=12, num_slow=26, num_signal=9) :
    filepath = './merged_data/trend_csvfiles'

    for elem in codes:
        data = pd.read_csv(filepath + "/{}t.csv".format(elem[1:]))

        data['EMAFast'] = data['close'].ewm(span=num_fast).mean()
        data['EMASlow'] = data['close'].ewm(span=num_slow).mean()
        data['MACD'] = data['EMAFast'] - data['EMASlow']
        data['MACDSignal'] = data['MACD'].ewm(span=num_signal).mean()
        data['MACDiff'] = data['MACD'] - data['MACDSignal']

        trend_data = data
        trend_data.to_csv(filepath+"/{}t.csv".format(elem[1:]), index=False)

    return trend_data


# RSI(Relative Strength Index) = 상대적 강도 지수
# 30 이하시 초과매도 매수 포지션을 취해야 하고, 70 이상시 초과매수 = 매도 포지션 취해야 한다.
# 50 을 기준으로 상향 돌파시 매수, 하향 돌파시 매도
def cal_RSI(codes, days=14):
    filepath = './merged_data/trend_csvfiles'

    for elem in codes:
        data = pd.read_csv(filepath + "/{}t.csv".format(elem[1:]))

        Up = np.where(data.diff(1)['close'] > 0, data.diff(1)['close'], 0)
        Down = np.where(data.diff(1)['close'] < 0, data.diff(1)['close'] * (-1), 0)

        AU = pd.DataFrame(Up).rolling(window=days, min_periods=days).mean()
        AD = pd.DataFrame(Down).rolling(window=days, min_periods=days).mean()

        RSI = AU / (AD+AU) * 100

        data['RSI'] = RSI

        trend_data = data
        trend_data.to_csv(filepath + "/{}t.csv".format(elem[1:]), index=False)

    return trend_data

def cal_BB(codes):
    filepath = './merged_data/trend_csvfiles'

    for elem in codes:
        data = pd.read_csv(filepath + "/{}t.csv".format(elem[1:]))

        data['upper_bb'] = data['ma20'] + (data['standard deviation20'] * 2) # 상단 볼린저 밴드
        data['mid_bb'] = data['standard deviation20'] # 중간 볼린저 밴드
        data['lower_bb'] = data['ma20'] - (data['standard deviation20'] * 2) # 하단 볼린저 밴드

        trend_data = data
        trend_data.to_csv(filepath + "/{}t.csv".format(elem[1:]), index=False)

    return trend_data

def cal_sto(codes, n=12, m=5, t=5):
    filepath = './merged_data/trend_csvfiles'

    for elem in codes:
        data = pd.read_csv(filepath + "/{}t.csv".format(elem[1:]))

        hp = data['high'].rolling(window=n).max()
        lp = data['low'].rolling(window=n).min()

        # %k = n일 중 가장 높은 종가를 100%, 가장 낮은 종가를 0%로 봤을 때, 현재 가격의 위치
        # %d = %k값의 m봉을 지수이동평균하여 이동평균선을 만들어 %d로 표시
        # fast_k = (종가 - n일중 최저가) / (n일중 최고가 - n일중 최저가) * 100
        fast_k = ((data['close'] - lp) / (hp - lp)) * 100
        slow_k = fast_k.ewm(span=m).mean() #
        slow_d = slow_k.ewm(span=t).mean() # t일 동안의 slow_k 의 평균

        data['fast_k'] = fast_k
        data['slow_k'] = slow_k
        data['slow_d'] = slow_d

        trend_data = data
        trend_data.to_csv(filepath + "/{}t.csv".format(elem[1:]), index=False)

    return trend_data

def cut_date(codes):
    filepath = './merged_data/trend_csvfiles'
    result_path = './merged_data/quarter_csvfiles'

    if not os.path.exists(result_path):
        os.mkdir(result_path)
    for elem in codes:
        data = pd.read_csv(filepath + "/{}t.csv".format(elem[1:]))
        data['date'] = data['date'].astype(str)

        bool1 = data['date']>='20110401'
        bool2 = data['date']<'20210101'

        trend_data = data[bool1&bool2]
        trend_data.to_csv(result_path + "/{}t.csv".format(elem[1:]), index=False)

    return trend_data

sql_to_csv()
select_cols_for_monkey()
cal_std()
cal_ma()
cal_MACD()
cal_RSI()
cal_BB()
cal_sto()
cut_date()