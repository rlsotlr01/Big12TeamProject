import os
import sys
import time
import win32com.client

import naver_crawling.naver_finance_crawling as nfc

from itertools import chain
from PyQt5.QtWidgets import *


# 복수 종목 실시간 조회 샘플 (조회는 없고 실시간만 있음)
class CpEvent:

    def set_params(self, client):
        self.client = client

    def OnReceived(self):
        code = self.client.GetHeaderValue(0)  # 코드
        name = self.client.GetHeaderValue(1)  # 종목명
        diff = self.client.GetHeaderValue(2)  # 전일대비
        t_time = self.client.GetHeaderValue(3)  # 전일대비
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
        date_time_sec = timess1 + str(self.client.GetHeaderValue(18)).zfill(6)  # 시간(초)
        exFlag = self.client.GetHeaderValue(19)  # 예상체결가구분플래그
        market_diff_flag = self.client.GetHeaderValue(20)  # 장구분플래그

        if (exFlag == ord('1')):  # 동시호가 시간 (예상체결)
            print("실시간(예상체결)", name, date_time_sec, "현재가", cur_price, "대비", diff, "t_time ", t_time)

        elif (exFlag == ord('2')):  # 장중(체결)
            print("실시간(장중 체결)", name, date_time_sec, "현재가", cur_price, "대비", diff, "t_time", t_time)

    def OnDisConnect(self):     # exe file 실행
        print('CpEvent 연결 끊김!!!')
        os.startfile('main.exe')
        exit()


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
            print(rpCode, rpName, rpTime, rpDiffFlag, rpDiff, rpCur, rpVol, cnt)

        return True

    def OnDisConnect(self):
        print('CpMarketEye 연결 끊김!!!')
        os.startfile('main.exe')
        exit()


class MyWindow(QMainWindow):

    def __init__(self):
        super().__init__()
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

        self.btnStart_clicked()     # 프로그램 실행하면 실시간 수집 시작

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

        # 요청 종목 배열 /
        codes_list = []
        request_list = ('IT서비스', '해운사', '조선', '광고', '건설', '게임엔터테인먼트', '은행', '손해보험', '생명보험', '증권',
                        '식품', '화장품', '백화점과일반상점', '석유와가스', '음료', '반도체와반도체장비', '기계', '자동차', '자동차부품', '가정용기기와용품',
                        '화학', '무선통신서비스', '복합기업', '전자장비와기기', '철강', '방송과엔터테인먼트', '항공사', '통신장비', '소프트웨어', '섬유,의류,신발,호화품',
                        '제약', '생명과학도구및서비스', '건축자재', '생물공학', '가스유틸리티')
        naver_codes = nfc.NaverFinanceCrawler()
        for request_ in request_list:
            codes_list.append(naver_codes.get_stock_code(request_))

        codes = list(chain(*codes_list))  # 모든 종목코드를 담음.

        # 요청 필드 배열 - 종목코드, 시간, 대비부호 대비, 현재가, 거래량, 종목명

        rqField = [0, 1, 2, 3, 4, 10, 17]  # 요청 필드
        objMarkeyeye = CpMarketEye()
        if (objMarkeyeye.Request(codes, rqField) == False):
            exit()

        cnt = len(codes)
        for i in range(cnt):
            self.objCur.append(CpStockCur())
            self.objCur[i].Subscribe(codes[i])

        print(cnt, "종목 실시간 현재가 요청 시작")
        self.isSB = True

    def btnStop_clicked(self):
        self.StopSubscribe()


    def btnExit_clicked(self):
        self.StopSubscribe()
        exit()


def start():
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
