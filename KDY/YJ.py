from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

def collect_data_info():

    driver = webdriver.Chrome('C:/Users/YJ/big12/note/driver/chromedriver.exe')
    driver.get('https://finance.naver.com/sise/sise_group_detail.nhn?type=upjong&no=204')

    driver.find_element_by_xpath('''//*[@id="option2"]''').click()

    click_per_xpath = '''//*[@id="option6"]'''
    driver.find_element_by_xpath(click_per_xpath).click()

    click_marketcap_xpath = '''//*[@id="option4"]'''
    driver.find_element_by_xpath(click_marketcap_xpath).click()

    driver.execute_script('javascript:fieldSubmit()')

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')


    base_url = 'https://finance.naver.com'                                              # 기본이 될 URL
    table = soup.find('table', attrs={'summary': '업종별 시세 리스트'})                     # 테이블 찾기
    name_list = table.find_all('div', attrs={'class': 'name_area'})                      # 테이블에서 종목 이름 가져오기
    target_url = [base_url + name.find('a')['href'] for name in name_list]              # 종목 URL
    name = [name.find('a').get_text() for name in name_list]                            #종목 이름
    print(name)
    print(len(name))

    tgs = table.find_all('tr')

    marketcap = [tg.find_all('td', class_='number')[7].text.strip() for tg in tgs if len(tg.find_all('td', class_='number')) > 1]      # 시가총액 모으기
    print(marketcap)
    print(len(marketcap))

    per = [tg.find_all('td', class_='number')[8].text.strip() for tg in tgs if len(tg.find_all('td', class_='number')) > 1]            # per 모으기
    print(per)
    print(len(per))

    '''
     종목 코드 : code
    - 코스피인지 코스닥인지 : class
    (내용물은 'kospi' 또는 'kosdaq' 으로 기입)
    - 종목 이름 : name
    - 시가총액 : market_cap
    - 상장일 : reg_day
    - PER : per (소수점 두 번째 자리까지)
    '''
    code = []
    market = []
    reg_day = []

    # 각 URL에 들어가서 종목코드, 시장정보(코스피,코스닥), 상장일 가져오기
    for target in target_url:
        driver.get(target)
        # 종목코드
        code_xpath = '''//*[@id="middle"]/div[1]/div[1]/div/span[1]'''
        code_info = driver.find_element_by_xpath(code_xpath).text
        code.append("A" + code_info)
        driver.implicitly_wait(3)
        # 시정정보(코스닥,코스피)
        market_info_xpath = '''//*[@id="middle"]/div[1]/div[1]/div/img'''
        market_info = driver.find_element_by_xpath(market_info_xpath).get_attribute('class')
        market.append(market_info)
        driver.implicitly_wait(3)
        # 상장일 가져오기
        reg_site = 'https://navercomp.wisereport.co.kr/v2/company/c1020001.aspx?cn=&cmp_cd={code_num}&menuType=block'.format(code_num=code_info)
        driver.get(reg_site)

        driver.implicitly_wait(3)
        reg_day_info = driver.find_element_by_xpath('//*[@id="cTB201"]/tbody/tr[3]/td[1]').text  # 상장일 찾아서
        reg_day.append(reg_day_info[-11:-1])
    driver.close()

    print(code)
    print(len(code))
    print(market)
    print(len(market))
    print(reg_day)
    print(len(reg_day))


    # 데이터프레임 만들기
    cols = [
        'name'
        , 'code'
        , 'class'
        , 'market_cap'
        , 'reg_day'
        , 'per'
    ]
    data_df = pd.DataFrame(
        {
             'name': collect_data_info().name
            ,'code': collect_data_info().code
            ,'class': collect_data_info().market
            ,'market_cap': collect_data_info().marketcap
            ,'reg_day': collect_data_info().reg_day
            ,'per': collect_data_info().per
        }
    )

    # 데이터 전처리
    data_df['market_cap'] = data_df['market_cap'].apply(lambda x: x.replace(',', ''))
    #data_df['per'] = round((data_df['per']), 3)


    return data_df

print(collect_data_info())
