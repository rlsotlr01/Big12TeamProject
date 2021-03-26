import win32com.client
import sqlite3


class StockKind:
    def __init__(self):
        # 연결 여부 체크
        objCpCybos = win32com.client.Dispatch("CpUtil.CpCybos")         # cybos 연결 체크
        bConnect = objCpCybos.IsConnect

        if bConnect == 0:
            print("PLUS가 정상적으로 연결되지 않음. ")
            exit()

        conn = sqlite3.connect("stock_kind.db", isolation_level=None)  # sqlite 연결
        self.c = conn.cursor()

        self.c.execute("CREATE TABLE IF NOT EXISTS STOCK_KIND (CODE text PRIMARY KEY, SECOND_CODE integer, NAME text)")  # 종목코드 & 서브코드 & 종목명 을 저장항 table 생성

    def start_collect(self):
        # 종목코드 리스트 구하기
        objCpCodeMgr = win32com.client.Dispatch("CpUtil.CpCodeMgr")
        codeList = objCpCodeMgr.GetStockListByMarket(1)  # 거래소
        codeList2 = objCpCodeMgr.GetStockListByMarket(2)  # 코스닥
        stock_list = []

        # db에 저장된 종목코드 load
        self.c.execute("SELECT CODE FROM STOCK_KIND")
        codes = self.c.fetchall()

        print("거래소 종목코드", len(codeList))
        print("번호 종목코드 2CODE 가격 종목명")
        for i, code in enumerate(codeList):
            secondCode = objCpCodeMgr.GetStockSectionKind(code)
            name = objCpCodeMgr.CodeToName(code)
            stdPrice = objCpCodeMgr.GetStockStdPrice(code)
            if not codes.__contains__(code):
                stock_list.append([code, secondCode, name])             # list에 추가

        print("코스닥 종목코드", len(codeList2))
        print("번호 종목코드 2CODE 가격 종목명")
        for i, code in enumerate(codeList2):
            secondCode = objCpCodeMgr.GetStockSectionKind(code)
            name = objCpCodeMgr.CodeToName(code)
            if not codes.__contains__(code):
                stock_list.append([code, secondCode, name])             # list에 추가

        print('start insert to db')
        for stock in stock_list:
            self.c.execute("INSERT OR IGNORE INTO STOCK_KIND VALUES( ?, ?, ?)", (stock[0], stock[1], stock[2]))
        print('finish insert to db')

        self.c.execute("SELECT CODE, NAME FROM STOCK_KIND")
        codes = self.c.fetchall()                       # 종목 코드를 tuple로 가져옴 ( fetchall은 tuple로 값을 반환 )
        self.c.close()
        print("거래소 + 코스닥 종목코드 ", len(codeList) + len(codeList2))
        return codes
