import win32com.client
import sqlite3

# 연결 여부 체크
objCpCybos = win32com.client.Dispatch("CpUtil.CpCybos")
bConnect = objCpCybos.IsConnect
if (bConnect == 0):
    print("PLUS가 정상적으로 연결되지 않음. ")
    exit()

# 종목코드 리스트 구하기
objCpCodeMgr = win32com.client.Dispatch("CpUtil.CpCodeMgr")
codeList = objCpCodeMgr.GetStockListByMarket(1)  # 거래소
codeList2 = objCpCodeMgr.GetStockListByMarket(2)  # 코스닥

#DB 생성
conn = sqlite3.connect("stock_price(day).db", isolation_level=None)

c = conn.cursor()
    # 테이블 생성 (테이블명은 코드이름)
c.execute("CREATE TABLE IF NOT EXISTS code_name"
              "(CODE text PRIMARY KEY, SECONDCODE text, NAME text)")
sql_sent = "INSERT OR IGNORE INTO code_name VALUES( ?, ?, ?)"

print("거래소 종목코드", len(codeList))
for i, code in enumerate(codeList):
    secondCode = objCpCodeMgr.GetStockSectionKind(code)
    name = objCpCodeMgr.CodeToName(code)
    c.execute(sql_sent, (code, secondCode, name))

print("코스닥 종목코드", len(codeList2))
for i, code in enumerate(codeList2):
    secondCode = objCpCodeMgr.GetStockSectionKind(code)
    name = objCpCodeMgr.CodeToName(code)
    c.execute(sql_sent, (code, secondCode, name))

print("거래소 + 코스닥 종목코드 ", len(codeList) + len(codeList2))