import sqlite3
import os
import pandas as pd
import openpyxl
import csv
from xlsxwriter.workbook import Workbook
import glob

def make_folder_for_result():
    # 결과물 담을 폴더 만들기.
    base = './merged_data'
    if not os.path.exists(base[2:]):
        # naver_data 폴더가 존재하지 않으면 해당 폴더를 만든다.
        os.mkdir(base)

# openpyxl 이용해서 퀀트킹 안에 담긴 code 불러오면,
# sql_to_csv 파일 사용해서 해당 code 의 데이터를 csv로 만들어주기 위한 용도

# db 안에 있는 데이터를 csv로 만들어주는 함수. (기능 완료)
def sql_to_csv(code):
    # code 는 A 포함하지 않고 넣어줘야 함. ex.005930 이렇게.
    # 사용할 데이터의 위치
    data_loc = './data'
    # 결과가 저장될 폴더를 만들어준다.
    make_folder_for_result()
    # 결과가 저장될 위치
    base = './merged_data'
    filepath = base+'/csvfiles'
    code = 'A'+code
    # csvfiles 폴더가 존재하지 않으면 해당 폴더를 만든다.
    if not os.path.exists(filepath):
        os.mkdir(filepath)
    db=sqlite3.connect(data_loc+'/stock_db(day)_merge.db')
    selected_data = pd.read_sql_query("SELECT * FROM {}".format(code), db)
    # 해당 코드의 csv 파일을 저장한다.
    selected_data.to_csv(filepath+"/{}.csv".format(code[1:]),index=False)
    return selected_data

# csv 를 불러와서 전처리 하기 위한 용도 (완료)
# - monkey 강화학습에 필요한 컬럼(day, cur_pr, high_pr, low_pr, clo_pr, for_stor만 뽑아내고,
# - 컬럼명 변경 (date, open, high, low, close, volume)
# - 날짜도 10년치로 추린다. (20110701~20201231)
def select_cols_for_monkey(code):
    # 날짜 20110701부터 20210101 전까지 데이터만 가져온다.
    filepath = './merged_data/csvfiles'
    result_path = './merged_data/processed_csvfiles'
    if not os.path.exists(result_path):
        os.mkdir(result_path)
    data = pd.read_csv(filepath+"/{}.csv".format(code))
    data['day']=data['day'].astype(str)
    new_data = data[['day','cur_pr','high_pr','low_pr','clo_pr','acc_vol']]
    bool1 = new_data['day']>='20110401'
    bool2 = new_data['day']<'20210101'

    processed_data = new_data[bool1&bool2]
    col_processed_data = processed_data.rename(columns = {'day':'date','cur_pr':'open','high_pr':'high','low_pr':'low','clo_pr':'close','acc_vol':'volume'})
    col_processed_data.to_csv(result_path+"/{}.csv".format(code),index=False)
    return col_processed_data

# 일단 이전에 종합 여기에 있는 엑셀파일을 다 005930.csv 형식으로 바꿔줘야 할 것 같은데.
# csv 안에 종목코드 정보가 담겨있으니깐 그거 따와서 이름을 그거로 정해주는 방식으로.

# csv 파일 excel 로 바꿔주는 함수
# filepath 폴더 위치 지정해주면 해당 폴더에 있는 csv 파일을 모두 xlsx 로 바꿔준다. (완료)
def csv_to_excel(filepath):
    stock_code_list = []
    save_loc = './merged_data/csv_to_excel'
    folder_names = filepath.split('/')[2:]
    # csv_to_excel 폴더 만들기
    if not os.path.exists(save_loc):
        os.mkdir(save_loc)
    # csv_to_excel 안에 폴더 만들기

    # 저장할 위치 폴더 만들어놓기
    new_loc = save_loc
    for folder_name in folder_names:
        new_loc += '/' + folder_name
        if not os.path.exists(new_loc):
            os.mkdir(new_loc)
    # new_loc = 저장 경로 (여기까진 성공)
    csvfiles = glob.glob(filepath + '/*.csv')
    for csvfile in csvfiles:
        read_file = pd.read_csv(csvfile, error_bad_lines=False, encoding='MS949')
        codeWithA = read_file.columns[2]
        read_file.to_excel(new_loc+'/{}.xlsx'.format(codeWithA[1:]),index=False)
        # 여기는 파일에 따라서 오류가 날 수가 있음.
        # 파일명을 지정해주는 부분은 각자 필요한 명명대로 바꿔줘야 함.

# 종목현황 엑셀파일에는 코드명이 다른 위치에 있어서 변경해줌.
# read_file.iloc[1,2] 이부분이 변경된 부분임.
# 그리고 주식 코드 리스트를 반환해준다.
def csv_to_excel_for_state_file(filepath):
    stock_code_list = []
    save_loc = './merged_data/csv_to_excel'
    folder_names = filepath.split('/')[2:]
    # csv_to_excel 폴더 만들기
    if not os.path.exists(save_loc):
        os.mkdir(save_loc)
    # csv_to_excel 안에 폴더 만들기

    # 저장할 위치 폴더 만들어놓기
    new_loc = save_loc
    for folder_name in folder_names:
        new_loc += '/' + folder_name
        if not os.path.exists(new_loc):
            os.mkdir(new_loc)
    # new_loc = 저장 경로 (여기까진 성공)
    csvfiles = glob.glob(filepath + '/*.csv')
    for csvfile in csvfiles:
        read_file = pd.read_csv(csvfile, error_bad_lines=False, encoding='MS949')
        codeWithA = read_file.iloc[1,2] # 해당 엑셀파일엔 iloc[1,2] 위치에 코드가 있어서 코딩 변경함.
        read_file.to_excel(new_loc+'/{}.xlsx'.format(codeWithA[1:]),index=False)
        # 만약 파일명 그대로 복사하고 싶을 경우는
        # read_file.to_excel(csvfile[:-4]+'.xlsx', index=False)
        # 이걸로 대체해주면 됨.

# 퀀트킹 엑셀로 변환된 파일(
# './merged_data/csv_to_excel/재무차트/종합'
# './merged_data/csv_to_excel/종목현황/종합'
# 에서 재무데이터 가져와
# 필요한 양식에 맞춰 바꿔주고, csv 파일로 저장해주는 함수
def quant_to_csv(code):
    date = pd.date_range(start='20110401', end='20201231', freq='3MS').to_list()
    data = pd.DataFrame(data=date, columns=['date'])

    # 워크북 엑셀시트 읽기기
    # https://tariat.tistory.com/781 참고
    finance_chart_wb = openpyxl.load_workbook('./merged_data/csv_to_excel/재무차트/종합/{}.xlsx'.format(code))
    code_state_wb = openpyxl.load_workbook('./merged_data/csv_to_excel/종목현황/종합/{}.xlsx'.format(code))

    finance_chart_ws = finance_chart_wb.active
    code_state_ws = code_state_wb.active

    company_name = finance_chart_ws['B1'].value
    company_code = finance_chart_ws['C1'].value[1:]
    roe = finance_chart_ws['P50':'BB50']
    roes = [re.value for re in roe[0]]
    roa = finance_chart_ws['P51':'BB51']
    roas = [ra.value for ra in roa[0]]
    eps = finance_chart_ws['P55':'BB55']
    epss = [es.value for es in eps[0]]
    bps = finance_chart_ws['P56':'BB56']
    bpss = [bs.value for bs in bps[0]]
    whole_sale = finance_chart_ws['P16':'BB16'] # 총 매출액
    whole_sales = [ws.value for ws in whole_sale[0]]
    quart_margin = finance_chart_ws['P17':'BB17'] # 분기 영업이익
    quart_margins = [qm.value for qm in quart_margin[0]]
    quart_net_margin = finance_chart_ws['P18':'BB18']
    quart_net_margins = [qn.value for qn in quart_net_margin[0]]
    dps = finance_chart_ws['P68':'BB68'] # 주당 배당금
    dpss = [ds.value for ds in dps[0]]
    debt_rate = finance_chart_ws['P72':'BB72'] # 부채 비율
    debt_rates = [dr.value for dr in debt_rate[0]]

    # 현금 흐름표
    run_act = finance_chart_ws['P76':'BB76'] # 영업활동
    run_acts = [ra.value for ra in run_act[0]]
    invest_act = finance_chart_ws['P77':'BB77'] # 투자 활동
    invest_acts = [ia.value for ia in invest_act[0]]
    fin_act = finance_chart_ws['P78':'BB78'] # 재무 활동
    fin_acts = [fa.value for fa in fin_act[0]]

    # # 종목현황에서 필요한 데이터 - 부채 총계 / 근데 연단위로 존재.
    # debt = code_state_ws['C96':'K96']



    # data['per']=~~
    # data['pcr']=~~
    # 이런 식으로 엑셀파일 안에 있는 데이터를 openpyxl로 읽어서 해당 분기별로
    # 데이터를 넣어줄 것.
    # 20170701 6.83
    # 20171001 4.32
    # 이런 식으로 분기별로.
    data['roe'] = roes
    data['roa'] = roas
    data['eps'] = epss
    data['bps'] = bpss
    data['sales'] = whole_sales
    data['margin'] = quart_margins
    data['net_margin'] = quart_net_margins
    data['dps'] = dpss
    data['debt_ratio'] = debt_rates
    data['run_money'] = run_acts
    data['invest_money'] = invest_acts
    data['financial_money'] = fin_acts

    save_loc = './merged_data/quarterly_quant_data'

    if not os.path.exists(save_loc):
        os.mkdir(save_loc)
    data.to_csv(save_loc+'/{}.csv'.format(code),index=False)

    return data

def get_codes_without_A():
    codes = glob.glob('./merged_data/csv_to_excel/재무차트/종합/*.xlsx')
    processed_codes = [code[-11:-5] for code in codes]
    return processed_codes

# 그리고 quant 엑셀파일들을 csv로 옮겨준 csv 파일을 pd.DataFrame 으로 불러와서,
# 분기에 맞도록 넣어줘야 함.
def merge_quant_and_daily(code):
    quant_finance_data_loc = './merged_data/quarterly_quant_data/{}.csv'.format(code)
    quant_finance_data = pd.read_csv(quant_finance_data_loc)
    daily_data_loc = './merged_data/processed_csvfiles/{}.csv'.format(code)
    daily_data = pd.read_csv(daily_data_loc)
    add_cols = quant_finance_data.columns[1:].to_list() # 날짜를 제외한다.
    daily_data['date'] = daily_data['date'].astype('str')
    daily_data[add_cols] = 0 # 넣기 전 초기화

    for idx in range(len(quant_finance_data['date'])):
        if (idx+1) < len(quant_finance_data['date']):
            front_date = quant_finance_data['date'][idx]
            back_date = quant_finance_data['date'][idx+1]
        else:
            front_date = quant_finance_data['date'][idx]
            back_date = '20210101'
        bool1 = daily_data['date'] >= front_date
        bool2 = daily_data['date'] < back_date
        for col in add_cols:
            daily_data.loc[bool1&bool2,col] = quant_finance_data[col].iloc[idx]
            # 해당 날짜 사이의 컬럼에
            # 해당 분기의 데이터를 넣어야 되는데.
    save_loc = './merged_data/final_merged_data'
    # csv_to_excel 폴더 만들기
    if not os.path.exists(save_loc):
        os.mkdir(save_loc)

    daily_data.sort_values(by='date',ascending=True, inplace=True) # 날짜순으로 정렬
    daily_data.to_csv(save_loc+'/{}f.csv'.format(code),index=False)
    return daily_data

