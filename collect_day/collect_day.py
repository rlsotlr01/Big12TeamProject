import win32com.client
import sqlite3
import time


class DayCollect:
    def __init__(self):
        # 연결 여부 체크
        self.objCpCybos = win32com.client.Dispatch("CpUtil.CpCybos")
        self.bConnect = self.objCpCybos.IsConnect
        if self.bConnect == 0:
            print("PLUS가 정상적으로 연결되지 않음. ")
            exit()

        self.objStockWeek = win32com.client.Dispatch("DsCbo1.StockWeek")

        self.conn = sqlite3.connect("stock_db(day).db", isolation_level=None)  # sqlite 연결
        self.c = self.conn.cursor()

    def __del__(self):
        self.c.close()

    def reqeustData(self, obj, code, idx = 0):
        # 데이터 요청
        obj.BlockRequest()

        # 통신 상태 확인
        self.rqStatus = obj.GetDibStatus()
        # print("통신상태", self.rqStatus, obj.GetDibMsg1())
        if self.rqStatus != 0:
            return False

        # 일자별 정보 데이터 처리
        self.count = obj.GetHeaderValue(1)  # 데이터 개수     36일씩 받아옴
        print(code[0], code[1], '가져온 데이터량 :', self.count, "통신상태", self.rqStatus, obj.GetDibMsg1(), idx, '회')
        for i in range(self.count):

            # if i % 35 == 0 and i != 0:
            #     time.sleep(1)
            day = obj.GetDataValue(0, i)            # 일자
            cur_pr = obj.GetDataValue(1, i)         # 시가
            high_pr = obj.GetDataValue(2, i)        # 고가
            low_pr = obj.GetDataValue(3, i)         # 저가
            clo_pr = obj.GetDataValue(4, i)         # 종가
            pr_diff = obj.GetDataValue(5, i)        # 전일대비
            acc_vol = obj.GetDataValue(6, i)        # 누적 거래량
            for_stor = obj.GetDataValue(7, i)       # 외인보유
            for_stor_diff = obj.GetDataValue(8, i)  # 외인보유전일대비
            for_perc = obj.GetDataValue(9, i)       # 외인비중
            com_buy_vol = obj.GetDataValue(12, i)   # 기관순매수수량
            oot_cur_pr = obj.GetDataValue(13, i)    # 시간외단일가시가
            oot_high_pr = obj.GetDataValue(14, i)   # 시간외단일가고가
            oot_low_pr = obj.GetDataValue(15, i)    # 시간외단일가저가
            oot_clo_pr = obj.GetDataValue(16, i)    # 시간외단일가종가
            oot_pr_diff = obj.GetDataValue(18, i)   # 시간외단일가전일대비
            oot_vol = obj.GetDataValue(19, i)       # 시간외단일가거래량
            for_buy_vol = obj.GetDataValue(21, i)   # 외국인 순매수 수량

            self.c.execute("INSERT OR IGNORE INTO " + code[0] + " VALUES( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                           (day, cur_pr, high_pr, low_pr, clo_pr, pr_diff, acc_vol, for_stor, for_stor_diff, for_perc, com_buy_vol, oot_cur_pr, oot_high_pr, oot_low_pr, oot_clo_pr, oot_pr_diff, oot_vol, for_buy_vol))
        return True

    # 일자별 데이터 가져오기
    def start_get_days_data(self, codes):
        last_index = 0
        for idx, code in enumerate(codes):
            self.c.execute('SELECT COUNT(*) FROM sqlite_master WHERE name="' + code[0]+'"')
            test = self.c.fetchall()
            if test[0][0] == 0:
                last_index = idx-1

                self.c.execute('delete from ' + codes[last_index][0])       # 중간에 끊긴 일별 데이터 테이블 삭제 후 다시 시작
                break

        # 일자별 data object 생성
        for index, code in enumerate(codes):          # 반복문을 통해
            if index < last_index:
                continue
            print('start insert to db : ' + code[0] + " : " + code[1])
            self.c.execute("CREATE TABLE IF NOT EXISTS " + code[0] + "(day integer PRIMARY KEY, cur_pr integer, "
                                                                     "high_pr integer, low_pr integer, clo_pr integer, "
                                                                     "pr_diff integer, acc_vol integer,"
                                                                     "for_stor integer, for_stor_diff integer, "
                                                                     "for_perc real, com_buy_vol integer, oot_cur_pr integer,"
                                                                     "oot_high_pr integer, oot_low_pr integer, oot_clo_pr integer,"
                                                                     "oot_pr_diff integer, oot_vol integer, for_buy_vol integer )")  # 종목코드 & 서브코드 & 종목명 을 저장항 table 생성

            self.objStockWeek.SetInputValue(0, code[0])  # 종목 코드설정.

            index = 1
            if self.reqeustData(self.objStockWeek, code, index):     # Data를 가져오는데 성공하면
                # 연속 데이터 요청
                while self.objStockWeek.Continue:       # 연속 조회처리
                    index += 1
                    ret = self.reqeustData(self.objStockWeek, code, index)
        self.conn.close()