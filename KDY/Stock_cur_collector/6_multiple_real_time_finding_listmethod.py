import sys
from PyQt5.QtWidgets import *
import win32com.client
import sqlite3
import time
import pandas as pd

# 복수 종목 실시간 조회 샘플 (조회는 없고 실시간만 있음)
class CpEvent:

    cnt2 = 0
    def set_params(self, client):
        self.client = client

    # 11시 12분 시작 - 1시 18분 종료 sk바사 10917 naver 19779 삼성생명 2495 삼성전자 23260 영원무역 711 삼성화재 1845
    def OnReceived(self):
        conn = sqlite3.connect("stock_price(cur).db", isolation_level=None)
        code = self.client.GetHeaderValue(0)  # 코드
        name = self.client.GetHeaderValue(1)  # 종목명
        diff = self.client.GetHeaderValue(2)  # 전일대비
        cur_price = self.client.GetHeaderValue(4)  # 시가
        high_price = self.client.GetHeaderValue(5)  # 고가
        low_price = self.client.GetHeaderValue(6)  # 저가
        sell_call = self.client.GetHeaderValue(7)  # 매도호가
        buy_call = self.client.GetHeaderValue(8)  # 매수호가
        acc_vol = self.client.GetHeaderValue(9)  # 누적거래량
        pred_price = self.client.GetHeaderValue(13)  # 현재가 또는 예상체결가
        deal_state = self.client.GetHeaderValue(14)  # 체결상태(체결가 방식)
        acc_sell_deal_vol = self.client.GetHeaderValue(15)  # 누적매도체결수량(체결가방식)
        acc_buy_deal_vol = self.client.GetHeaderValue(16)  # 누적매수체결수량(체결가방식)
        moment_deal_vol = self.client.GetHeaderValue(17)  # 순간체결수량
        timess1 = time.strftime('%Y%m%d')
        date_time_sec = timess1 + str(self.client.GetHeaderValue(18))  # 시간(초)
        exFlag = self.client.GetHeaderValue(19)  # 예상체결가구분플래그
        market_diff_flag = self.client.GetHeaderValue(20)  # 장구분플래그

        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS " + code +
                  " (diff real, cur_price integer, high_price integer, low_price integer"
                  ", sell_call integer, buy_call integer, acc_vol integer, pred_price integer, deal_state text, acc_sell_deal_vol integer"
                  ", acc_buy_deal_vol integer , moment_deal_vol integer ,date_time_sec text, exFlag text, market_diff_flag text )")

        # 여기에 필요한 데이터에 따라 컬럼명 변경
        # 컬럼명 바꿔줘야 함.
        # time 은 무조건

        sql_sent = "INSERT OR IGNORE INTO " + code + " VALUES( ?, ?, ?, ?, ?, ?)"
        print(sql_sent)
        self.cnt2 += 1

        if (exFlag == ord('1')):  # 동시호가 시간 (예상체결)

            #c.execute("CREATE TABLE IF NOT EXISTS BUYING_NUM "
            #          "(COMPNAME text, TIME text, PRICE integer, DIFF integer, BUYNUM integer, BUYNUM_ACC integer)")
            c.execute(
                "INSERT OR IGNORE INTO " + code + " VALUES( ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                ((diff,cur_price,high_price,low_price,sell_call,
                  buy_call,acc_vol,pred_price,deal_state,acc_sell_deal_vol,
                  acc_buy_deal_vol,moment_deal_vol,
                  date_time_sec,exFlag,market_diff_flag)))


            # 여기도

        elif (exFlag == ord('2')):  # 장중(체결)
            c.execute(
                "INSERT OR IGNORE INTO " + code + " VALUES( ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                ((diff, cur_price, high_price, low_price, sell_call,
                  buy_call, acc_vol, pred_price, deal_state, acc_sell_deal_vol,
                  acc_buy_deal_vol, moment_deal_vol,
                  date_time_sec, exFlag, market_diff_flag)))
            # 여기다가 넣을거 추가해야 함.

class CpStockCur:
    def Subscribe(self, code):
        self.objStockCur = win32com.client.Dispatch("DsCbo1.StockCur")
        handler = win32com.client.WithEvents(self.objStockCur, CpEvent)
        self.objStockCur.SetInputValue(0, code)
        handler.set_params(self.objStockCur)
        self.objStockCur.Subscribe()

    def Unsubscribe(self):
        self.objStockCur.Unsubscribe()


class CpMarketEye:
    def Request(self, codes, rqField):
        # 연결 여부 체크
        objCpCybos = win32com.client.Dispatch("CpUtil.CpCybos")
        bConnect = objCpCybos.IsConnect
        if (bConnect == 0):
            print("PLUS가 정상적으로 연결되지 않음. ")
            return False

        # 관심종목 객체 구하기
        objRq = win32com.client.Dispatch("CpSysDib.MarketEye")
        # 요청 필드 세팅 - 종목코드, 종목명, 시간, 대비부호, 대비, 현재가, 거래량
        # rqField = [0,17, 1,2,3,4,10]
        objRq.SetInputValue(0, rqField)  # 요청 필드
        objRq.SetInputValue(1, codes)  # 종목코드 or 종목코드 리스트
        objRq.BlockRequest()

        # 현재가 통신 및 통신 에러 처리
        rqStatus = objRq.GetDibStatus()
        rqRet = objRq.GetDibMsg1()
        print("통신상태", rqStatus, rqRet)
        if rqStatus != 0:
            return False

        cnt = objRq.GetHeaderValue(2)

        for i in range(cnt):
            rpCode = objRq.GetDataValue(0, i)  # 코드
            rpName = objRq.GetDataValue(1, i)  # 종목명
            rpTime = objRq.GetDataValue(2, i)  # 시간
            rpDiffFlag = objRq.GetDataValue(3, i)  # 대비부호
            rpDiff = objRq.GetDataValue(4, i)  # 대비
            rpCur = objRq.GetDataValue(5, i)  # 현재가
            rpVol = objRq.GetDataValue(6, i)  # 거래량
            print(rpCode, rpName, rpTime, rpDiffFlag, rpDiff, rpCur, rpVol,cnt)

        return True


class MyWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        conn = sqlite3.connect("stock_price(cur).db", isolation_level=None)
        # c = conn.cursor()
        self.setWindowTitle("PLUS API TEST")
        self.setGeometry(300, 300, 300, 150)
        self.isSB = False
        self.objCur = []

        btnStart = QPushButton("요청 시작", self)
        btnStart.move(20, 20)
        btnStart.clicked.connect(self.btnStart_clicked)

        btnStop = QPushButton("요청 종료", self)
        btnStop.move(20, 70)
        btnStop.clicked.connect(self.btnStop_clicked)

        btnExit = QPushButton("종료", self)
        btnExit.move(20, 120)
        btnExit.clicked.connect(self.btnExit_clicked)

    def StopSubscribe(self):
        if self.isSB:
            cnt = len(self.objCur)
            for i in range(cnt):
                self.objCur[i].Unsubscribe()
            print(cnt, "종목 실시간 해지되었음")
        self.isSB = False

        self.objCur = []

    def btnStart_clicked(self):
        self.StopSubscribe()

        # 요청 종목 배열
        conn = sqlite3.connect("stock_price(cur).db", isolation_level=None)
        c = conn.cursor()
        c.execute("select code from code_name")
        #codes = c.fetchall()
        # c.fetchall 의 데이터타입은 list
        codes_list = []
        data = pd.read_csv('./naver_data/반도체와반도체장비.csv')
        codes = list(data['code'])
        #count11 = 0
        for code in codes:
            #count11 += 1
            codes_list.append(code)
            #if count11>199 :
            #    break
        # 실시간데이터는 199개까지로 제한. 200개 부턴 안됨.
        # 위에는 DB에서 종목코드 가져오는 코딩. 제대로 작동함.
        codes = codes_list # 모든 종목코드를 담음.
        # 이거 db에서 가져올까?
        # 요청 필드 배열 - 종목코드, 시간, 대비부호 대비, 현재가, 거래량, 종목명

        rqField = [0, 1, 2, 3, 4, 10, 17]  # 요청 필드
        objMarkeyeye = CpMarketEye()
        if (objMarkeyeye.Request(codes, rqField) == False):
            exit()

        cnt = len(codes)
        for i in range(cnt):
            self.objCur.append(CpStockCur())
            self.objCur[i].Subscribe(codes[i])

        print("빼기빼기================-")
        print(cnt, "종목 실시간 현재가 요청 시작")
        self.isSB = True

    def btnStop_clicked(self):
        self.StopSubscribe()

    def btnExit_clicked(self):
        self.StopSubscribe()
        exit()


if __name__ == "__main__":

    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
