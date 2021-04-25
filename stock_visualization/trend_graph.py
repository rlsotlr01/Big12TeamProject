import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# csv 파일 디렉토리
v3_path = 'D:/PycharmProjects/Big12TeamProject/rltrader_second_trial/data/v3'

def draw_close_graph(code):
    data = pd.read_csv(v3_path + '/{}t.csv'.format(code))
    # date 컬럼 값을 int형에서 str로 변환
    data['date'] = data['date'].astype(str)
    # 변환된 str값을 날짜로 인식하도록 변환
    data['date'] = pd.to_datetime(data['date'])

    df = pd.DataFrame(data, columns=['date', 'close'])
    df = df.set_index('date')

    plt.subplot(211)
    plt.plot(df.index, data['close'], label='Close')

    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title('Close Price')

    plt.legend(loc='best')
    plt.grid()
    plt.show()

    return data

def draw_macd_graph(code):
    data = pd.read_csv(v3_path + '/{}t.csv'.format(code))
    # date 컬럼 값을 int형에서 str로 변환
    data['date'] = data['date'].astype(str)
    # 변환된 str값을 날짜로 인식하도록 변환
    data['date'] = pd.to_datetime(data['date'])

    df = pd.DataFrame(data, columns=['date', 'close'])
    df = df.set_index('date')

    plt.subplot(211)
    plt.plot(df.index, data['close'], label='Close')

    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title('Close Price')

    plt.grid()
    df = pd.DataFrame(data, columns=['date', 'MACD', 'MACDSignal'])
    df = df.set_index('date')

    plt.subplot(212)
    plt.plot(df.index, data['MACD'], label='MACD')
    plt.plot(df.index, data['MACDSignal'], label='MACDSignal')
    # plt.plot(df.index, data['MACDiff'], label='MACDiff')

    plt.xlabel('Date')
    plt.ylabel('MACD')
    plt.title('MACD')

    plt.legend(loc='best')
    plt.grid()
    plt.show()

    return data

# 이동평균선 그래프 시각화
def draw_ma_graph(code):
    data = pd.read_csv(v3_path+'/{}t.csv'.format(code))
    # date 컬럼 값을 int형에서 str로 변환
    data['date'] = data['date'].astype(str)
    # 변환된 str값을 날짜로 인식하도록 변환
    data['date'] = pd.to_datetime(data['date'])

    df = pd.DataFrame(data, columns=['date','ma5','ma10','ma20','ma60','ma120'])
    df = df.set_index('date')

    plt.plot(df.index, data['close'], label='Close')
    plt.plot(df.index, data['ma5'], label='MA5')
    plt.plot(df.index, data['ma10'], label='MA10')
    plt.plot(df.index, data['ma20'], label='MA20')
    plt.plot(df.index, data['ma60'], label='MA60')
    plt.plot(df.index, data['ma120'], label='MA120')

    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title('Market Average')

    plt.legend(loc='best')
    plt.grid()
    plt.show()

    return data

def draw_bb_graph(code):
    data = pd.read_csv(v3_path+'/{}t.csv'.format(code))
    # date 컬럼 값을 int형에서 str로 변환
    data['date'] = data['date'].astype(str)
    # 변환된 str값을 날짜로 인식하도록 변환
    data['date'] = pd.to_datetime(data['date'])

    df = pd.DataFrame(data, columns=['date','lower_bb','mid_bb','upper_bb'])
    df = df.set_index('date')

    plt.subplot(212)
    plt.plot(df.index, data['close'], label='Close')
    plt.plot(df.index, data['lower_bb'], label='lower_bb')
    plt.plot(df.index, data['mid_bb'], label='mid_bb')
    plt.plot(df.index, data['upper_bb'], label='upper_bb')

    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title('Bollinger Bands')

    plt.legend(loc='best')
    plt.grid()
    plt.show()

    return data

def draw_rsi_graph(code):
    data = pd.read_csv(v3_path+'/{}t.csv'.format(code))
    # date 컬럼 값을 int형에서 str로 변환
    data['date'] = data['date'].astype(str)
    # 변환된 str값을 날짜로 인식하도록 변환
    data['date'] = pd.to_datetime(data['date'])

    df = pd.DataFrame(data, columns=['date', 'close'])
    df = df.set_index('date')

    plt.subplot(211)
    plt.plot(df.index, data['close'], label='Close')

    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title('Close Price')

    plt.grid()

    df = pd.DataFrame(data, columns=['date','RSI'])
    df = df.set_index('date')

    plt.subplot(212)
    plt.plot(df.index, data['RSI'], color='orange', label='rsi')

    plt.xlabel('Date')
    plt.ylabel('RSI')
    plt.title('RSI')

    plt.legend(loc='best')
    plt.grid()
    plt.show()

    return data

def draw_sto_graph(code):
    data = pd.read_csv(v3_path+'/{}t.csv'.format(code))
    # date 컬럼 값을 int형에서 str로 변환
    data['date'] = data['date'].astype(str)
    # 변환된 str값을 날짜로 인식하도록 변환
    data['date'] = pd.to_datetime(data['date'])

    df = pd.DataFrame(data, columns=['date', 'close'])
    df = df.set_index('date')

    plt.subplot(211)
    plt.plot(df.index, data['close'], label='Close')

    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title('Close Price')

    plt.grid()

    df = pd.DataFrame(data, columns=['date','fast_k','slow_k','slow_d'])
    df = df.set_index('date')

    plt.subplot(212)
    plt.plot(df.index, data['fast_k'], color='red', label='fast%k')
    plt.plot(df.index, data['slow_k'], color='orange', label='slow%k')
    plt.plot(df.index, data['slow_d'], color='blue', label='slow%d')

    plt.xlabel('Date')
    plt.ylabel('Stochastic')
    plt.title('Stochastic Oscillator')

    plt.legend(loc='best')
    plt.grid()
    plt.show()

    return data

# draw_close_graph('009830')
# draw_ma_graph('009830')
draw_macd_graph('009830')
# draw_bb_graph('009830')
# draw_rsi_graph('009830')
# draw_sto_graph('009830')