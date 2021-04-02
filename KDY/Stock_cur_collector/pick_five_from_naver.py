# Writer : Dongyoon Kim
# Date : 210401
# Description : Collecting the best five company which satisfy several conditions
#               from Naver in each industrial fields
from datetime import datetime
from selenium import webdriver
import random
import pandas as pd
import time
from bs4 import BeautifulSoup
import os
import glob

# 업종별 이름과 사이트 가져오는 라이브러리
##### 업종별 이름, 사이트 다 모으기.
def collect_links_of_each_field():
    # 크롬드라이버가 연결되어 있는 주소 저장
    chromedriver = 'C:\chromedriver_win32\chromedriver.exe'
    # 크롬드라이버 연결
    driver = webdriver.Chrome(chromedriver)
    # 업종 사이트 연결
    driver.get('https://finance.naver.com/sise/sise_group.nhn?type=upjong')
    # 업종의 tbody에는 업종별로 사이트를 저장하는 a태그들이 있다. 그것을 꺼낸다.
    a_tags = driver.find_element_by_tag_name('tbody').find_elements_by_tag_name('a')
    category_list = []
    # 업종의 주소와 이름을 저장
    for a in a_tags:
        category_list.append([a.get_attribute('href'), a.text])
    # 구글 드라이버를 꼭 닫아주기.
    driver.close()
    return category_list

# 네이버 증권 홈페이지에서 한 업종페이지의 url을 받아 데이터를 수집하는 함수.
# 업종명과 판다스데이터프레임을 출력해준다.
def collect_data_from_naver(url):
    driver = webdriver.Chrome('C:\chromedriver_win32\chromedriver.exe') #크롬을 사용할거다
    driver.get(url) #열어라

    # 네이버 표시 버튼을 클릭하여 필요한 정보만 나오도록 해준다.
    buy_btn_xpath = '//*[@id="option2"]'
    sell_btn_xpath = '//*[@id="option8"]'
    marketcap_btn_xpath = '//*[@id="option4"]'
    per_btn_xpath = '//*[@id="option6"]'
    apply_btn_xpath = '//*[@id="contentarea"]/div[3]/form/div/div/div/a[1]/img'
    driver.find_element_by_xpath(buy_btn_xpath).click() # buy버튼 클릭
    driver.find_element_by_xpath(sell_btn_xpath).click() # sell버튼 클릭
    driver.find_element_by_xpath(marketcap_btn_xpath).click() # 시가총액 버튼 클릭
    driver.find_element_by_xpath(per_btn_xpath).click() # per버튼 클릭
    driver.find_element_by_xpath(apply_btn_xpath).click() # 적용하기 버튼 클릭


    driver.implicitly_wait(3)

    # PER 을 표시해주는 버튼을 클릭한다.

    company_table_xpath = '//*[@id="contentarea"]/div[4]/table'
    company_table = driver.find_element_by_xpath(company_table_xpath)
    # 테이블을 찾고

    # 셀레늄이 들어가있는 홈페이지의 html 데이터를 뷰티풀숩으로 넘겨주는 코드
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # 해당 html 에서 테이블을 찾는다. (업종데이터들이 담긴 표)
    table = soup.find('table', attrs={'summary':'업종별 시세 리스트'})

    # url 가져오기
    base_url = 'https://finance.naver.com'
    name_lists = table.find_all('div', attrs={'class':'name_area'})
    links = [base_url+name.find('a')['href'] for name in name_lists]
    name = [name.find('a').get_text() for name in name_lists]
    # 회사명과 회사로 통하는 링크를 받아온다.

    # 시가총액, PER 가져오기
    trs = table.find_all('tr')
    marketcap = [tr.find_all('td',class_='number')[6].text.strip() for tr in trs if len(tr.find_all('td',class_='number'))>1]
    per = [tr.find_all('td',class_='number')[7].text.strip() for tr in trs if len(tr.find_all('td',class_='number'))>1]
    # 테이블별 각각의 항목(tr)을 모두 가져오고ㅡ
    # tr 중에서 td를 가져오되, class 이름이 number 인 것만 가져온다. (숫자데이터)
    # 그 중에서 시가총액(6번 인덱스) ,PER(7번 인덱스) 두 데이터를 뽑아 각각의 리스트에 담아준다.

    # 길이가 0 이상인 것만 더해준다.

    code = []
    reg_date = [] # 상장일
    class__ = []
    # 이제 해당 링크를 타고 가서 종목코드와 상장일을 가져온다.

    industrial_field_xpath = '//*[@id="contentarea_left"]/table/tbody/tr[4]/td[1]'
    industrial_field = driver.find_element_by_xpath(industrial_field_xpath).text

    # 링크 리스트를 받아서 해당 링크에서 필요한 종목정보들을 가져온다.
    for link in links:
        driver.get(link)
    #    html = driver.page_source
    #   여기선 셀레늄으로 데이터 추출해보자.
        kospi_xpath = '//*[@id="middle"]/div[1]/div[1]/div/img'
        kospi_or_kosdaq = driver.find_element_by_xpath(kospi_xpath).get_attribute('class')
        class__.append(kospi_or_kosdaq)
        code_num = driver.find_element_by_xpath('//*[@id="middle"]/div[1]/div[1]/div/span[1]').text
        code.append("A"+code_num)

        # 코스피 코스닥 정보 가져오기

        code_analysis_btn_xpath = '//*[@id="content"]/ul/li[6]/a/span' # 종목분석 버튼
        driver.find_element_by_xpath(code_analysis_btn_xpath).click()  # 종목분석 버튼 클릭
        # 기업개요는 안찾아짐. 어떻게 들어가지?
        driver.implicitly_wait(3)
        reg_site = 'https://navercomp.wisereport.co.kr/v2/company/c1020001.aspx?cn=&cmp_cd={code}&menuType=block'.format(code=code_num)
        driver.get(reg_site)

        driver.implicitly_wait(3)
        reg_day = driver.find_element_by_xpath('//*[@id="cTB201"]/tbody/tr[3]/td[1]').text # 상장일 찾아서
        reg_date.append(reg_day[-11:-1])


    # pd.DataFrame(data, columns=[comp_names[0],comp_names[]])
    cols = ['name','code','class','market_cap','reg_day','per']
    data = pd.DataFrame(
        {
            'name':name
            , 'code':code
            , 'class':class__
            , 'market_cap':marketcap
            , 'reg_day':reg_date
            , 'per':per
        }
    )

    data['market_cap'] = data['market_cap'].apply(lambda x: x.replace(",", ""))
    # 데이터 전처리 (숫자 사이에 ',' 없애기)

    return industrial_field, data
# 업종이름이랑 data 를 리턴하면 될 것 같은데?

# 업종명과 판다스 데이터프레임을 받아 csv 파일로 추출해주는 기능
def store_total_data(industrial_field, pd_data):
    base = './naver_data'
    filename = '/' + industrial_field + '전체.csv'

    if not os.path.exists('naver_data'):
        # naver_data 폴더가 존재하지 않으면 해당 폴더를 만든다.
        os.mkdir(base)

    pd_data.to_csv(
        base+filename
        , encoding='utf-8'
    )
    # 이제 csv 파일로 저장해야 됨. 업종이름 셀레늄으로 가져오는게 좋을 듯.

# String 데이터를 날짜 데이터로 변환해주는 기능.
def string_to_date(string):
    day = datetime.strptime(string, '%Y/%m/%d')
    return day


# 이제 조건처리 등등 해야 함.
# naver_data 폴더 안에서 csv 파일을 하나하나 꺼내 데이터프레임으로 만들어주고,
# 해당 데이터프레임을 이용해 조건처리하고,
# 조건처리가 완성된 데이터프레임을 따로 '업종.csv' 로 저장해준다.


# 1. 설립한지 10년 이상인가
datetime.now() # 현재시간에서 설립일 빼줘서 3650일 이상
# 2. 코스피인가
# 세 조건 모두 만족하는 시가총액 상위 5개를 뽑기
def selecting_with_conditions(year, kospi_or_kosdaq, how_many_comp):
    csv_files = glob.glob('./naver_data/*전체.csv')
    for csv_file in csv_files:
        # ./naver_data\\반도체와반도체장비전체.csv 
        # 파일명에서 업종명만 가져온다. - 반도체와반도체장비 만 가져옴
        data = pd.read_csv(csv_file)
        industrial_field_name = csv_file[13:-6]

    # 데이터 전처리하기
    # 1.날짜 문자열을 날짜데이터로 바꿔준다.
    data['reg_day'] = pd.to_datetime(data['reg_day'])
    reg_day = pd.to_datetime(data['reg_day'])

    # 2. 시가총액 문자열을 정수로 바꿔준다.
    data['market_cap'] = data['market_cap'].astype('int')
    market_cap = data['market_cap']

    # boolean 하나하나 만들어서 마지막에 불리언 인덱싱 하기.


    # 1. 설립한지 ?년(year) 이상 되었는지
    # 설립일을 담아준다.

    # 현재 날짜와 설립일 사이의 날짜 차이를 구한다.
    day_diff = datetime.now() - reg_day
    days = day_diff.dt.days # 일수만 뽑아준다
    days_boolean = days > 365*year # ?년 이상 된 기업만 가져온다.

    # kospi인지 kosdaq인지
    kos_boolean = (data['class']==kospi_or_kosdaq)

    # 시가총액 상위 몇개의 기업을 가져올 것인지
    collected_data = data[days_boolean & kos_boolean]
    top_companies = collected_data.sort_values(by='market_cap', ascending=False).head(how_many_comp)
    base = './naver_data'
    filename = '/' + industrial_field_name + '.csv'
    # 반도체및반도체장비.csv 이런 식으로 저장해준다.
    top_companies.to_csv(
        base+filename
        , encoding='utf-8'
    )
    #   ex) how_many_comp = 5 : 상위 5개

# 모든 업종별 종목정보 csv 저장하고, 
# 각 업종별 조건에 맞는 데이터만 뽑아서 또 csv로 저장해주는 모듈
def collecting_all():
    category_list = collect_links_of_each_field()
    # 카테고리명과 카테고리별 링크를 담아준다.
    # ex ) [https://www.f~~~~, 반도체및반도체장비] ... 이런 식으로
    category_links = []
    for category in category_list:
        category_links.append(category[0])

    url = 'https://finance.naver.com/sise/sise_group_detail.nhn?type=upjong&no=202'
    for url in category_links:
        industrial_field, pd_data = collect_data_from_naver(url)
        # 해당 url에 들어가 데이터를 수집하고, 업종명과 해당 업종들의 종목정보가 담긴 판다스데이터프레임 산출해준다.
        store_total_data(industrial_field, pd_data)
        # 업종명과 판다스데이터프레임을 통해 csv 파일을 만들어준다.
        selecting_with_conditions(10, 'kospi', 5)
        # 10년 이상, kospi 이고, 시총 상위 5개 기업을 가져온다.

    # 조건처리의 경우는 data 라는 폴더 안에 있는 ~~~전체 로 되어 있는 csv 파일을 모두 불러와서,
    # 조건처리 하고, 업종 값으로 다시 저장하는 메소드를 만들면 좋을 것 같음.


# 카테고리명과 카테고리별 링크를 담아준다.
# ex ) [https://www.f~~~~, 반도체및반도체장비] ... 이런 식으로


# 반도체만 가져오기
url = 'https://finance.naver.com/sise/sise_group_detail.nhn?type=upjong&no=202'
industrial_field, pd_data = collect_data_from_naver(url)
# 해당 url에 들어가 데이터를 수집하고, 업종명과 해당 업종들의 종목정보가 담긴 판다스데이터프레임 산출해준다.
store_total_data(industrial_field, pd_data)
# 업종명과 판다스데이터프레임을 통해 csv 파일을 만들어준다.
selecting_with_conditions(10,'kospi',5)
# 10년 이상, kospi 이고, 시총 상위 5개 기업을 가져온다.


# 모든 업종별 조건처리 맞는 데이터들 가져오기
# collecting_all()