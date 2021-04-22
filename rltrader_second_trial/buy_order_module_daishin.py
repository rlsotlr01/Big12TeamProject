import win32com.client

def order_stocks(code, buy, num_stocks, price):
    # code : 종목코드 숫자만.
    # buy_or_sell : 행동 - 1 매수 2 매도
    # num_stocks : 주식 몇개 살거냐.
    # 연결 여부 체크

    # 신경망의 행동 상수와 API의 행동 상수 값이 다르기에 치환해준다.
    if buy == 0:
        action = 2
    elif buy == 1:
        action = 1
    # ACTION_BUY = 0  # 매수
    # ACTION_SELL = 1  # 매도
    # ACTION_HOLD = 2 # 홀드

    # 여기 API에선 1이 매도 2가 매수

    codewithA = 'A'+code
    objCpCybos = win32com.client.Dispatch("CpUtil.CpCybos")
    bConnect = objCpCybos.IsConnect
    if (bConnect == 0):
        print("PLUS가 정상적으로 연결되지 않음. ")
        exit()

    # 주문 초기화
    objTrade = win32com.client.Dispatch("CpTrade.CpTdUtil")
    initCheck = objTrade.TradeInit(0)
    if (initCheck != 0):
        print("주문 초기화 실패")
        exit()

    # 주식 매수 주문
    acc = objTrade.AccountNumber[0]  # 계좌번호
    accFlag = objTrade.GoodsList(acc, 1)  # 주식상품 구분
    print(acc, accFlag[0])
    objStockOrder = win32com.client.Dispatch("CpTrade.CpTd0311")
    objStockOrder.SetInputValue(0, action)  # 1: 매도 / 2: 매수
    objStockOrder.SetInputValue(1, acc)  # 계좌번호
    objStockOrder.SetInputValue(2, accFlag[0])  # 상품구분 - 주식 상품 중 첫번째
    objStockOrder.SetInputValue(3, codewithA)  # 종목코드 - A003540 - 대신증권 종목
    objStockOrder.SetInputValue(4, num_stocks)  # 매수수량 10주

    # 주문단가는 실시간 가격 조회에서 가져와야 함.

    objStockOrder.SetInputValue(5, price)  # 주문단가  - 14,100원
    objStockOrder.SetInputValue(7, "0")  # 주문 조건 구분 코드, 0: 기본 1: IOC 2:FOK
    objStockOrder.SetInputValue(8, "01")  # 주문호가 구분코드 - 01: 보통

    # 매수 주문 요청
    objStockOrder.BlockRequest()

    rqStatus = objStockOrder.GetDibStatus()
    rqRet = objStockOrder.GetDibMsg1()
    print("통신상태", rqStatus, rqRet)
    if rqStatus != 0:
        exit()



