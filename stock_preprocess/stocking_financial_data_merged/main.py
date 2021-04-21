import data_merger_module

filepath = './data/재무차트/종합'
filepath2 = './data/종목현황/종합'

# 퀀트킹 데이터를 excel 로 바꿔줄 때 사용하는 용도.
# 만약에 csv_to_excel 에 어떤 파일도 존재하지 않는다면 아래 코드를 실행해야 함.
#csv_to_excel(filepath)
#csv_to_excel_for_state_file(filepath2)


codes = data_merger_module.get_codes_without_A()
for code in codes:
    data_merger_module.sql_to_csv(code) # db에 있는 해당 종목의 일별 데이터를 csv 로 옮겨줌.
    data_merger_module.select_cols_for_monkey(code) # db에서 옮긴 일별 데이터를 조건에 맞게 전처리해줌.
    data_merger_module.quant_to_csv(code) # 분기별로 되어 있는 퀀트 데이터를 사용하기에 알맞게 정리해줌.
    data_merger_module.merge_quant_and_daily(code) # 퀀트 데이터와 일별 데이터를 합쳐줌.

# 그리고 최종적으로 합쳐진 데이터는 final_merged_data 폴더로 들어가게 됩니다.
# final_merged_data 는 주식 강화학습에 사용될 수 있는 데이터입니다.
