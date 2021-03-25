import win32com.client
import sqlite3

def RequestData(obj, code):
    # 데이터 요청 - 데이터를 하나하나 다 출력하고, 만약 데이터가 없으면 false 를 반환하고 함수 끝낸다.
    # 그리고 입력값으로 code(종목코드)를 넣으면 해당 코드의 일일 종목정보를 가지고 온다.
    obj.BlockRequest()

    # 통신 결과 확인
    rqStatus = obj.GetDibStatus()
    rqRet = obj.GetDibMsg1()
    print("통신상태", rqStatus, rqRet)
    if rqStatus != 0:
        return False

    # 일자별 정보 데이터 처리
    count = obj.GetHeaderValue(1)  # 데이터 개수
    print('카운트 : ',count)

    sql_sent = "INSERT OR IGNORE INTO " + code + " VALUES( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?" \
                                                 ", ?, ?, ?, ?, ?, ?, ?)"
    conn = sqlite3.connect("stock_price(day).db", isolation_level=None)
    c = conn.cursor()
    for i in range(count):
        day = obj.GetDataValue(0, i)  # 일자
        cur_pr = obj.GetDataValue(1, i)  # 시가
        high_pr = obj.GetDataValue(2, i)  # 고가
        low_pr = obj.GetDataValue(3, i)  # 저가
        clo_pr = obj.GetDataValue(4, i)  # 종가
        pr_diff = obj.GetDataValue(5, i)  # 종가
        acc_vol = obj.GetDataValue(6, i)  # 누적 거래량
        for_stor = obj.GetDataValue(7, i) # 외인 보유
        for_stor_diff = obj.GetDataValue(8, i) # 외인 보유 전일 대비
        for_perc = obj.GetDataValue(9, i) # 외인 비중
        com_buy_vol = obj.GetDataValue(12, i) # 기관 순매수 수량
        oot_cur_pr = obj.GetDataValue(13, i) # 시간외 단일가 시가
        oot_high_pr = obj.GetDataValue(14, i) # 시간외 단일가 고가
        oot_low_pr = obj.GetDataValue(15, i) # 시간외 단일가 저가
        oot_clo_pr = obj.GetDataValue(16, i) # 시간외 단일가 종가
        oot_pr_diff = obj.GetDataValue(18, i) # 시간외 단일가 전일대비
        oot_vol = obj.GetDataValue(19, i) # 시간외 단일가 거래량
        c.execute(sql_sent, (day, cur_pr, high_pr, low_pr, clo_pr, pr_diff,
                             acc_vol, for_stor, for_stor_diff,
                             for_perc, com_buy_vol, oot_cur_pr, oot_high_pr,
                             oot_low_pr, oot_clo_pr, oot_pr_diff, oot_vol))

    return True



# 연결 여부 체크
objCpCybos = win32com.client.Dispatch("CpUtil.CpCybos")
bConnect = objCpCybos.IsConnect
if (bConnect == 0):
    print("PLUS가 정상적으로 연결되지 않음. ")
    exit()

#DB 생성
conn = sqlite3.connect("stock_price(day).db", isolation_level=None)
c = conn.cursor()
c.execute("select code from code_name limit 600 offset 600")
codes = c.fetchall()
# c.fetchall 의 데이터타입은 list
codes_list = []
for code in codes:
    codes_list.append(code[0])
        # 위에는 DB에서 종목코드 가져오는 코딩. 제대로 작동함.
codes = codes_list # 모든 종목코드를 담음.
# 찾고 싶은 종목의 목록을 넣어준다
# stock_price(day).db 안에 code_name 테이블에서 종목코드를 가져와서
# codes 변수에 리스트로 담아준다. 이 기능 만들기.

for code in codes:
    # 일자별 object 구하기
    objStockWeek = win32com.client.Dispatch("DsCbo1.StockWeek")
    # 일별데이터를 구할 땐 DsCbo1 안에 StockWeek 모듈을 사용한다.
    c = conn.cursor()
    # 테이블 생성 (테이블명은 코드이름)
    c.execute("CREATE TABLE IF NOT EXISTS " + code +
              "(DAY date PRIMARY KEY, CUR_PR integer, HIGH_PR integer, LOW_PR integer, CLO_PR integer"
              ", PR_DIFF integer, ACC_VOL integer, FOR_STOR integer, FOR_STOR_DIFF integer"
              ", FOR_PERC real, COM_BUY_VOL integer, OOT_CUR_PR integer, OOT_HIGH_PR integer"
              ", OOT_LOW_PR integer, OOT_CLO_PR integer, OOT_PR_DIFF integer, OOT_VOL integer)")
    sql_sent = "INSERT OR IGNORE INTO " + code + " VALUES( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?" \
                                                 ", ?, ?, ?, ?, ?, ?, ?)"
#   17개 데이터

    objStockWeek.SetInputValue(0, code)  # 종목 코드 - 삼성전자
    # 0번 위치에 종목코드를 입력한다.

    # 최초 데이터 요청
    ret = RequestData(objStockWeek, code)
    # 해당 종목의 데이터가 있는지 확인한다.

    if ret == False:
        # 해당 종목의 데이터가 없으면 나간다.
        exit()

    # 연속 데이터 요청 (API에서 한번에 36개까지만 가능하도록 해줌.)
    # 예제는 5번만 연속 통신 하도록 함.
    NextCount = 1
    while objStockWeek.Continue:
        # 연속 조회처리 - 36일치 한번 불러올 때마다 NextCount 1씩 더해짐.
        NextCount += 1;
        if (NextCount > 1000000000000000):
            break
        ret = RequestData(objStockWeek, code)
        if ret == False:
            exit()


# 0 - (date) 일자 - day
#
# 1 - (INTEGER) 시가 - cur_pr
#
# 2 - (INTEGER) 고가 - high_pr
#
# 3 - (INTEGER) 저가 - low_pr
#
# 4 - (INTEGER) 종가 - clo_pr
#
# 5 - (INTEGER) 전일대비 - pr_diff
#
# 6 - (INTEGER) 누적거래량 - acc_vol
#
# 7 - (INTEGER) 외인보유 - for_stor
#
# 8 - (INTEGER) 외인보유전일대비 - for_stor_diff
#
# 9 - (REAL) 외인비중 - for_perc
#
# 12- (INTEGER) 기관순매수수량 - com_buy_vol
#
# 13- (INTEGER) 시간외단일가시가 - oot_cur_pr
#
# 14- (INTEGER) 시간외단일가고가 - oot_high_pr
#
# 15- (INTEGER) 시간외단일가저가 - oot_low_pr
#
# 16- (INTEGER) 시간외단일가종가 - oot_clo_pr
#
# 18- (INTEGER) 시간외단일가전일대비 - oot_pr_diff
#
# 19- (INTEGER) 시간외단일가거래량 - oot_vol