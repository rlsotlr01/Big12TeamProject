import win32com.client
import sqlite3


class RealTimeCollect:
    instance = None

    def __init__(self):
        self.objStockCur = CpStockCur()
        conn = sqlite3.connect("stock_kind.db", isolation_level=None)  # sqlite 연결
        self.c = conn.cursor()

    def OnReceived(self):
        timess = RealTimeCollect.instance.GetHeaderValue(18)  # 초
        exFlag = RealTimeCollect.instance.GetHeaderValue(19)  # 예상체결 플래그
        c_price = RealTimeCollect.instance.GetHeaderValue(13)  # 현재가
        diff = RealTimeCollect.instance.GetHeaderValue(2)  # 대비
        cVol = RealTimeCollect.instance.GetHeaderValue(17)  # 순간체결수량
        vol = RealTimeCollect.instance.GetHeaderValue(9)  # 거래량

        if exFlag == ord('1'):  # 동시호가 시간 (예상체결)
            print("실시간(예상체결)", timess, "*", c_price, "대비", diff, "체결량", cVol, "거래량", vol)
        elif exFlag == ord('2'):  # 장중(체결)
            print("실시간(장중 체결)", timess, c_price, "대비", diff, "체결량", cVol, "거래량", vol)


    def Request(self, code):
        # 연결 여부 체크
        objCpCybos = win32com.client.Dispatch("CpUtil.CpCybos")
        bConnect = objCpCybos.IsConnect
        if bConnect == 0:
            print("PLUS가 정상적으로 연결되지 않음. ")
            return False

        # 현재가 객체 구하기
        objStockMst = win32com.client.Dispatch("DsCbo1.StockMst")
        objStockMst.SetInputValue(0, code)  # 종목 코드
        objStockMst.BlockRequest()

        # 현재가 통신 및 통신 에러 처리
        rqStatus = objStockMst.GetDibStatus()
        rqRet = objStockMst.GetDibMsg1()
        print("통신상태", rqStatus, rqRet)
        if rqStatus != 0:
            return False

        # 현재가 정보 조회
        code = objStockMst.GetHeaderValue(0)  # 종목코드
        name = objStockMst.GetHeaderValue(1)  # 종목명
        time = objStockMst.GetHeaderValue(4)  # 시간
        c_price = objStockMst.GetHeaderValue(11)  # 종가
        diff = objStockMst.GetHeaderValue(12)  # 대비
        s_price = objStockMst.GetHeaderValue(13)  # 시가
        high = objStockMst.GetHeaderValue(14)  # 고가
        low = objStockMst.GetHeaderValue(15)  # 저가
        offer = objStockMst.GetHeaderValue(16)  # 매도호가
        bid = objStockMst.GetHeaderValue(17)  # 매수호가
        vol = objStockMst.GetHeaderValue(18)  # 거래량
        vol_value = objStockMst.GetHeaderValue(19)  # 거래대금

        print("코드 이름 시간 현재가 대비 시가 고가 저가 매도호가 매수호가 거래량 거래대금")
        print(code, name, time, c_price, diff, s_price, high, low, offer, bid, vol, vol_value)
        return True

    def start_collect_real_time_data(self):
        self.c.execute("SELECT CODE, NAME FROM STOCK_KIND")
        codes = self.c.fetchall()  # 종목 코드와 종목명을 tuple로 가져옴 ( fetchall은 tuple로 값을 반환 )

        for code in codes:
            if not self.Request(code[0]):
                return False
            self.objStockCur.Subscribe(code[0])
        self.c.close()

    def stop_collect_real_time_data(self):
        self.objStockCur.Unsubscribe()


class CpStockCur:
    def __init__(self):
        self.objStockCur = win32com.client.Dispatch("DsCbo1.StockCur")

    def Subscribe(self, code):
        win32com.client.WithEvents(self.objStockCur, RealTimeCollect)
        self.objStockCur.SetInputValue(0, code)
        RealTimeCollect.instance = self.objStockCur
        self.objStockCur.Subscribe()

    def Unsubscribe(self):
        self.objStockCur.Unsubscribe()
