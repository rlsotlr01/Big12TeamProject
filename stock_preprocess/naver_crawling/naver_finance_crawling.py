# naver_finance_crawling.py

import bs4
import re
import time
import pandas as pd
from tqdm import tqdm
from urllib.request import urlopen
from datetime import datetime
from dateutil.relativedelta import relativedelta


class NaverFinanceCrawler:  # 네이버 증권 크롤링 클래스
    def __init__(self):
        self.upjong_name_list = []  # 네이버 업종 리스트
        self.code_name_list = []    # 네이버 종목 리스트
        self.upjong_code_list = []  # 네이버 업종 코드 리스트

        self.base_url = 'https://finance.naver.com/'
        self.upjong_sub_url = 'sise/sise_group.nhn?type=upjong'
        self.upjong_url_list = []
        self.last_upjong = None
        self.last_company = None

        self.my_date = (datetime.today() + relativedelta(years=-10)).__format__('%Y%m%d')       # 10년 기준일

    def init(self):
        page = urlopen(self.base_url + self.upjong_sub_url)
        soup = bs4.BeautifulSoup(page, 'html.parser', from_encoding='euc-kr')
        self.upjong_list = soup.find_all('td', style='padding-left:10px;')
        print(self.upjong_list)

    def get_upjong(self):  # 업종가져오기
        self.init()

        for upjong in self.upjong_list:
            tmp = upjong.a['href'].split('=')

            self.upjong_code_list.append(tmp[len(tmp) - 1])  # 네이버 업종별 코드
            self.upjong_name_list.append(upjong.a.string)  # 업종명
            self.upjong_url_list.append(upjong.a['href'])  # 업종별 url

    def upjong_tour(self):  # 업종별로 종목정보 가져오기
        for url, upjong_name in tqdm(zip(self.upjong_url_list, self.upjong_name_list)):  # 업종 순회 for문
            if upjong_name is '기타':
                continue

            self.df_upjong = pd.DataFrame(
                columns=['code', 'class', 'name', 'market_cap', 'reg_day', 'per']
            )

            print('업종 시작 :', upjong_name, '=========================================')
            page = urlopen(self.base_url + url)
            soup = bs4.BeautifulSoup(page, 'html.parser', from_encoding='euc-kr')
            company_list = soup.find_all('td', class_='name')

            for company in tqdm(company_list):  # 업종별 종목 순회 for문
                if self.last_company is not None and company is not self.last_company:  # 중간에 끊겼다면
                    continue
                elif self.last_company is not None and company == self.last_company:
                    self.last_company = None

                code = company.a['href'].split('=')[1]  # 종목코드 split
                if not self.get_comany_info(code, company.a.string):
                    print('======================================================================= except')
                    print(upjong_name, '========================================================== except')
                    print(company.a.string, '===================================================== except')
                    print('======================================================================= except')
                    self.last_company = company.a.string
                    self.last_upjong = upjong_name
                    time.sleep(15)
                    return False
            self.df_upjong.to_csv(upjong_name + '.csv', encoding='utf-8', sep=',')
        return True

    def get_comany_info(self, company_code, company_name):  # 종목별 정보 가져오기
        try:
            co_page = urlopen(self.base_url + 'item/coinfo.nhn?code=' + company_code)  # 종목 분석 페이지
            soup = bs4.BeautifulSoup(co_page, 'html.parser', from_encoding='euc-kr')

            code = company_code
            print('\n' + company_name, 'code', code)

            class_ = ''
            if soup.find_all('img', alt='코스닥'):
                class_ = 'kosdaq'
            elif soup.find_all('img', alt='코스피'):
                class_ = 'kospi'
            print('class', class_)

            market_cap = soup.find(id='_market_sum').string.strip().replace(',', '')  # 시가총액
            pattern = re.compile(r'\s+')  # 정규식 사용하여 모든 공백 제거
            market_cap = re.sub(pattern, '', market_cap)

            if market_cap.__contains__('조'):  # 조단위일때 처리
                tmp = market_cap.split('조')
                market_cap = tmp[0] + tmp[1].zfill(4)

            print('market_cap', market_cap)

            per = soup.find(id='_per')  # per이 None이면 - 를 대입
            if per is not None:
                per = per.string
            else:
                per = '-'
            print('per', per)

            co_page = urlopen('https://navercomp.wisereport.co.kr/v2/company/c1020001.aspx?cmp_cd=' + company_code + '&cn=', timeout=15)
            soup = bs4.BeautifulSoup(co_page, 'html.parser', from_encoding='utf-8')
            reg_day = soup.find_all('td', class_='c2 txt')

            reg = ''
            for c2 in reg_day:  # 상장일 가져오기
                if c2.string is not None:
                    if c2.string.__contains__('상장일'):
                        days = c2.string.strip().split()
                        reg_day = days[len(days) - 1].split(')')[0].replace('/', '')
                        break
            if type(reg_day) == bs4.element.ResultSet:
                reg_day = '-'
            print('reg_day', reg_day)
            print(code, class_, company_name, market_cap, reg_day, per)
            self.df_upjong.loc[len(self.df_upjong)] = ['A' + code, class_, company_name, market_cap, reg_day, per]

            print('---------------------------------\n')
            return True
        except Exception as e:
            print('error :', e)
            print(company_name, '======================================================== except')
            return False

    # 업종명을 param으로 받고 10년 기준일보다 오래된, 시가총액 상위 5개 회사의 종목코드리스트를 리턴
    def get_stock_code(self, upjong_name):
        stock_df = pd.read_csv(upjong_name + '.csv', encoding='utf-8')
        stock_df = stock_df[stock_df['reg_day'] < int(self.my_date)]
        stock_df = stock_df.sort_values('market_cap', ascending=False)
        result = stock_df['code'][:5].tolist()
        return result

if __name__ == "__main__":
    tst = NaverFinanceCrawler()
    tst.get_upjong()
    while not tst.upjong_tour():
        tst.init()
        tst.upjong_tour()
    print('fin')
