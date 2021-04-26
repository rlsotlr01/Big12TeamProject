import datetime as dt
from collections import defaultdict

import pandas as pd
import win32com.client

from fipc import fcfg as cfg
from fipc import futil as util

# setting for trading
acc = cfg.acc

cpstkcd = win32com.client.Dispatch("CpUtil.CpStockCode")
itnum = cpstkcd.GetCount()  # this line is req. for run stockChart. dummy itcode

cptrade = win32com.client.Dispatch("CpTrade.CpTd0311")



# StockMst, get curr values
cpstkm = win32com.client.Dispatch("dscbo1.StockMst")

# MarketEye
cpmeye = win32com.client.Dispatch("CpSysDib.MarketEye")

# cpfitr - 외국인(f)/기관(insti~) 매수 동향
cpfitr = win32com.client.Dispatch("CpSysDib.CpSvrNew7215A")

cntrad = 0  # check trading


def init_trade():
    cptrdinit = win32com.client.Dispatch("CpTrade.CpTdUtil")
    if cptrdinit.TradeInit() != 0:
        print("fail to init trading")
        return False
    return True


# get item by names (or code)
def get_items(bycode=True):
    items = []
    dtype = 0 if bycode else 1
    for idx in range(itnum):
        item = cpstkcd.GetData(dtype, idx)
        items.append(item)
    return items


def get_itcode(itname):
    return cpstkcd.NameToCode(itname)


def get_itname(itcode):
    return cpstkcd.CodeToName(itcode)


def get_portfolio():
    # create obj. and init to call
    cptrd = win32com.client.Dispatch("CpTrade.CpTd6033")
    cptrd.SetInputValue(0, acc)
    cptrd.SetInputValue(1, '01')

    # req
    cptrd.BlockRequest()

    # 잔고 조회
    evalr = cptrd.GetHeaderValue(11)

    # res
    dfraw = defaultdict(list)
    cnt = cptrd.GetHeaderValue(7)
    cdl = []
    for i in range(cnt):
        quantity = cptrd.GetDataValue(7, i)  # 체결잔고수량
        price = int(cptrd.GetDataValue(17, i))  # 체결장부단가
        evalue = cptrd.GetDataValue(9, i)  # 평가금액
        profit = cptrd.GetDataValue(11, i)  # 수익률
        code = cptrd.GetDataValue(12, i)  # 종목코드
        dfraw['quantity'].append(quantity)
        dfraw['price'].append(price)
        dfraw['eval'].append(evalue)
        dfraw['profit'].append(profit)  # %
        cdl.append(code)

    return pd.DataFrame(dfraw, index=cdl), evalr


def get_item(itcode):
    # req.
    cpstkm.SetInputValue(0, itcode)
    cpstkm.BlockRequest()

    # set fields from req.
    itvals = dict()
    price = cpstkm.GetHeaderValue(11)  # 현재가
    stocknum = cpstkm.GetHeaderValue(31)  # 발행주
    ttag = cpstkm.GetHeaderValue(67)  # 투자경고구분 : 정상/주이/경고/위험예고/위험
    ttype = cpstkm.GetHeaderValue(45)  # 소속 구분 (코스닥, 거래소 등)
    per = cpstkm.GetHeaderValue(28)  # PER
    bps = cpstkm.GetHeaderValue(70)  # BPS

    itvals['name'] = get_itname(itcode)
    itvals['code'] = itcode
    itvals['price'] = price
    itvals['stocknum'] = int(stocknum)
    itvals['ttag'] = util.to_str_ttag(ttag)
    itvals['ttype'] = util.to_str_ttype(ttype)
    itvals['per'] = per
    itvals['pbr'] = price / bps if bps != 0 else 0

    return itvals


def get_curp(itcode):
    return get_item(itcode)['price']


def get_tseries(itcode, count=-1, ctype='D', start=dt.date.today() + dt.timedelta(days=-1), to=dt.date.today()):
    cpsc = win32com.client.Dispatch("CpSysDib.StockChart")

    # set values for calling cpsc
    cpsc.SetInputValue(0, itcode)

    if count == -1 or count == '-1':
        # req by duration
        cpsc.SetInputValue(1, ord('1'))
        cpsc.SetInputValue(3, int(util.to_date_str(start)))
        cpsc.SetInputValue(2, int(util.to_date_str(to)))
    else:
        # num of req. data
        cpsc.SetInputValue(1, ord('2'))
        cpsc.SetInputValue(4, count)

    # set fields
    fields = (0, 2, 3, 4, 5, 8)  # can be list instead of tuple
    cpsc.SetInputValue(5, fields)

    # chart type
    cpsc.SetInputValue(6, ord(ctype))
    if ctype == 'm':
        cpsc.SetInputValue(7, cfg.tick)

    # adjusted value
    cpsc.SetInputValue(9, ord('1'))

    # req. by block mode
    cpsc.BlockRequest()

    # header value
    numdata = cpsc.GetHeaderValue(3)
    numfields = cpsc.GetHeaderValue(1)

    # get data
    dfraw = defaultdict(list)

    fname = {0: 'date', 1: 'time', 2: 'open', 3: 'high', 4: 'low', 5: 'close',
             8: 'volume'}
    for i in range(numdata):
        for j in range(numfields):
            value = cpsc.GetDataValue(j, numdata - i - 1)  # reserving
            dfraw[fname[fields[j]]].append(value)

    tsdf = pd.DataFrame(dfraw)
    tsdf['date'] = pd.to_datetime(tsdf['date'], format='%Y%m%d').dt.date
    tsdf = tsdf.set_index('date')

    return tsdf


def buy(itcode, quantity, price, ttype='normal'):
    # risk control to limit trading number
    global cntrad

    if cntrad >= cfg.max_cnt_trading:
        print('over trading')
        return

    cptrade.SetInputValue(0, '2')  # 매수
    cptrade.SetInputValue(1, acc)  # 계좌번호
    cptrade.SetInputValue(2, '01')  # 상품관리구분코드
    cptrade.SetInputValue(3, itcode)  # 종목코드
    cptrade.SetInputValue(4, quantity)  # 주문수량

    if ttype == 'normal':
        cptrade.SetInputValue(5, price)
        cptrade.SetInputValue(8, '01')  # 보통 주문방식

    cptrade.BlockRequest()
    cntrad += 1

    print('req. for buying item: %s, quantity: %s, price: %s' % (itcode, quantity, price))


def sell(itcode, quantity, price, ttype='normal'):
    # init
    cptrs = win32com.client.Dispatch("CpTrade.CpTd0311")
    cptrs.SetInputValue(0, '1')
    cptrs.SetInputValue(1, acc)
    cptrs.SetInputValue(2, '01')
    cptrs.SetInputValue(3, itcode)
    cptrs.SetInputValue(4, quantity)  # 주문수량

    if ttype == 'normal':
        cptrs.SetInputValue(5, price)
        cptrs.SetInputValue(8, '01')  # 보통 주문방식

    # req
    cptrs.BlockRequest()

    util.debuglog('req. for selling item: %s, quantity: %s, price: %d' % (itcode, quantity, price))


if __name__ == "__main__":
    init_trade()
    import time
    for _ in range(30):
        print(get_portfolio())
        time.sleep(10)

    print(get_curp('A168330'))
