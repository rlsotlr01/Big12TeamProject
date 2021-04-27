# investing_crawling.py

import os
import shutil
import time

import sqlite3
import numpy as np
import pandas as pd
from selenium import webdriver


class InvestingCrawler:
    def __init__(self):
        self.base_url = 'https://kr.investing.com/'

        self.login_id = '아이디'       # csv 다운로드를 위해 로그인이 필수
        self.login_pw = '비밀번호'                  # 구글, 페이스북 로그인이 아닌 이메일 회원가입으로 동작하게 작성됨

        self.kospi_url = 'indices/kospi-historical-data'

        self.dollar_index_url = 'currencies/us-dollar-index-historical-data'
        self.dollar_won_url = 'currencies/usd-krw-historical-data'
        self.euro_won_url = 'currencies/eur-krw-historical-data'
        self.jap_won_url = 'currencies/jpy-krw-historical-data'
        self.cny_won_url = 'currencies/cny-krw-historical-data'

        self.gold_url = 'commodities/gold-historical-data'
        self.wti_url = 'commodities/crude-oil-historical-data'

        self.nasdaq_url = 'indices/nasdaq-composite-historical-data'
        self.dowjones_url = 'indices/us-spx-500-historical-data'
        self.euro_stocks_url = 'indices/eu-stoxx50-historical-data'
        self.nikkei_url = 'indices/japan-ni225-historical-data'

        self.hangsen_url = 'indices/hang-sen-40-historical-data'

        self.usa_2years_url = 'rates-bonds/us-2-yr-t-note-historical-data'
        self.usa_5years_url = 'rates-bonds/us-5-yr-t-note-historical-data'
        self.usa_10years_url = 'rates-bonds/us-10-yr-t-note-historical-data'
        self.usa_30years_url = 'rates-bonds/us-30-yr-t-bond-historical-data'

        # 수집할 데이터 url list. DB에 입력할 컬럼순으로
        self.download_list = [self.kospi_url, self.dollar_won_url, self.euro_won_url, self.jap_won_url,
                              self.dollar_index_url, self.cny_won_url, self.gold_url, self.wti_url, self.nasdaq_url,
                              self.dowjones_url, self.euro_stocks_url, self.nikkei_url, self.hangsen_url,
                              self.usa_2years_url, self.usa_5years_url, self.usa_10years_url, self.usa_30years_url]

        # 수집한 데이터 파일명 및 DB 컬럼명. 위 url 순서와 맞춰서 입력해야함
        self.new_file_name_list = ['kospi', 'dollar', 'euro', 'jap',
                                   'dollaridx', 'cny', 'gold', 'wti', 'nasdaq',
                                   'dowjones', 'eurostock', 'nikkei', 'hangsen',
                                   'usa2', 'usa5', 'usa10', 'usa30']

        self.login_xpath = '''//*[@id="userAccount"]/div/a[1]'''
        self.promote_login_xpath = '''//*[@id="PromoteSignUpPopUp"]/div[2]/div/a'''
        self.login_confirm_btn_xpath = '''//*[@id="signup"]/a'''

        self.download_xpath = '''//*[@id="column-content"]/div[4]/div/a'''
        self.date_select_xpath = '''//*[@id="widgetFieldDateRange"]'''
        self.start_date_xpath = '''element_select_date'''
        self.date_choice_id = 'datePickerIconWrap'
        self.apply_btn_xpath = '''//*[@id="applyBtn"]'''

        self.options = webdriver.ChromeOptions()        # download 폴더 변경을 위해 선언
        self.options.add_experimental_option("prefs", { # 위치 확인할 것
            "download.default_directory": r"F:\StockProject\investing_crawling"
        })

        self.filepath = 'F:\StockProject\investing_crawling\\'      # 다운로드할 위치

        self.conn = sqlite3.connect("global.db", isolation_level=None)  # sqlite 연결
        self.c = self.conn.cursor()

    def login(self, driver):        # 로그인
        login_btn = driver.find_element_by_xpath(self.login_xpath)      # 페이지 상단의 login 버튼
        if login_btn is None:
            login_btn = driver.find_element_by_xpath(self.promote_login_xpath)  # 팝업형식으로 뜨는 로그인
        login_btn.click()

        input_id = driver.find_element_by_id('loginFormUser_email')     # id 텍스트박스 선택
        input_id.send_keys(self.login_id)                               # id 입력

        input_pw = driver.find_element_by_id('loginForm_password')      # pw 텍스트박스 선택
        input_pw.send_keys(self.login_pw)                               # pw 입력

        btn_login = driver.find_element_by_xpath(self.login_confirm_btn_xpath)  # login 확인 버튼
        btn_login.click()

    def start_crawling(self, start_date, end_date):  # 크롤링 시작. 시작일과 종료일 입력받음
        driver = webdriver.Chrome('../driver/chromedriver.exe', chrome_options=self.options)    # driver 파일 확인하세요
        driver.get(self.base_url)

        self.login(driver)
        driver.implicitly_wait(20)

        for download, name in zip(self.download_list, self.new_file_name_list):     # url과 저장할 이름을 순서대로 & db 컬럼순
            driver.get(self.base_url + download)
            element_select_date = driver.find_element_by_xpath(self.date_select_xpath)  # 날짜 선택
            element_select_date.click()

            element_start_date = driver.find_element_by_xpath('''//*[@id="startDate"]''')   # 시작일 입력
            element_start_date.clear()
            element_start_date.send_keys(start_date)

            element_end_date = driver.find_element_by_xpath('''//*[@id="endDate"]''')       # 종료일 입력
            element_end_date.clear()
            element_end_date.send_keys(end_date)

            element_apply = driver.find_element_by_xpath(self.apply_btn_xpath)      # 기간 적용 버튼
            element_apply.click()

            time.sleep(5)   # 사이트의 데이터 로딩을 기다리는 시간. wait없이 바로 다운로드하면 가끔 아무값도 들어가지 않음

            btn_download = driver.find_element_by_xpath(self.download_xpath)        # 다운로드 버튼
            btn_download.click()

            time.sleep(5)

            # 다운로드한 파일이름 변경
            filename = max([self.filepath + '\\' + f for f in os.listdir(self.filepath)], key=os.path.getctime)
            shutil.move(os.path.join(self.filepath, filename), name + '.csv')

            driver.implicitly_wait(5)
        driver.close()
        InvestingCrawler().merge_data()

    def merge_data(self):  # 받은 데이터를 하나로 합치고 DB & csv로 저장
        df_db = pd.DataFrame()

        for idx, name in enumerate(self.new_file_name_list):

            df = pd.read_csv(self.filepath + name + '.csv', header=0, sep=',')

            columns = df.columns.tolist()   # 모든 csv파일의 컬럼이 날짜, 종가 순으로 되어있기에 명시적으로 컬럼명 수정
            columns[0] = 'date'
            columns[1] = name

            df.columns = columns

            df[name] = df[name].apply(lambda x : self.check_na(x))

            if idx == 0:        # 첫 데이터(kospi)를 기준으로 잡고
                df_db = df.iloc[:, :2]
            else:               # 이후 데이터부터 merge 시작
                df_db = pd.merge(df_db, df.iloc[:, :2], on='date', how='left')  # kospi 날짜를 기준

        df_db.fillna(method='bfill', inplace=True)  # 이전 데이터로 앞의 데이터를 채운 후 (4월 2일 데이터가 없을 경우 4월 1일 데이터로 4월 2일 데이터를 채움 )
        df_db.fillna(method='ffill', inplace=True)  # 앞의 데이터로 이전 데이터를 채움 (유로 스톡의 경우 2011년 8월부터 데이터가 있기 때문에 이전 데이터로 공백기간을 매워준다)

        # date 컬럼을 기준으로 내림차순, 원본데이터 반영
        df_db.sort_values(by='date', ascending=True, inplace=True)

        # 공백, 년, 월, 일 제거하기. 한줄로 가능
        df_db['date'] = df_db['date'].apply(lambda x: x.replace(' ', '')).apply(lambda x: x.replace('년', ''))\
            .apply(lambda x: x.replace('월', '')).apply(lambda x: x.replace('일', ''))
        start_time = time.time()
        df_db.to_sql('global', self.conn, if_exists='replace', index=False)
        df_db.to_csv('global.csv', sep=',')
        end_time = time.time()

        print('total save time :', end_time - start_time)   # db로 저장하는데 꽤 많은 시간이 들어감

    # - 값이 들어있는 경우 na로 바꿔주는 함수
    def check_na(self, x):
        if x == '-':
            return np.nan
        return x

if __name__ == "__main__":
    # InvestingCrawler().start_crawling('2011/04/01', '2020/12/31')   # 데이터 크롤링 시작. 시작 & 종료일 입력해야하며, 형식 맞춰야함(YYYY/MM/DD)
    InvestingCrawler().merge_data() # 받은 데이터를 합치는 함수