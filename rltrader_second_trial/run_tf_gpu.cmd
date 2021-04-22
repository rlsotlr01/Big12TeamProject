REM 삼성전자:005930 NAVER:035420 LG화학:051910 현대차:005380 셀트리온:068270 한국전력:015760
REM  

REM A2C
python main.py --stock_code 005930 --rl_method a2c --net lstm --num_steps 5 --output_name c_005930 --learning --num_epoches 1000 --lr 0.001 --start_epsilon 1 --discount_factor 0.9
python main.py --stock_code 005380 --rl_method a2c --net lstm --num_steps 5 --output_name c_005380 --learning --num_epoches 1000 --lr 0.001 --start_epsilon 1 --discount_factor 0.9
python main.py --stock_code 015760 --rl_method a2c --net lstm --num_steps 5 --output_name c_015760 --learning --num_epoches 1000 --lr 0.001 --start_epsilon 1 --discount_factor 0.9

REM A3C
python main.py --stock_code 005930 005380 015760 --rl_method a3c --net lstm --num_steps 5 --learning --num_epoches 1000 --lr 0.001 --start_epsilon 1 --discount_factor 0.9 --output_name train --start_date 20170101 --end_date 20181231

REM Testing
python main.py --stock_code 005380 --rl_method a2c --net lstm --num_steps 5 --output_name test_005380 --num_epoches 1 --start_epsilon 0 --start_date 20180101 --end_date 20181231 --reuse_models --value_network_name a2c_lstm_policy_b_005380 --policy_network_name a2c_lstm_value_b_005380


test 할 것
보험주
python main.py --stock_code 005830 000060 000810 003690 001450 --rl_method a3c --net lstm --num_steps 10 --learning False --num_epoches 1000 --lr 0.0001 --start_epsilon 0.3 --discount_factor 0.9 --reuse_models --output_name insurance_210420 --value_network_name a2c_lstm_value_b_insurance --policy_network_name a2c_lstm_policy_b_insurance --start_date 20110901 --end_date 20200901

DB손해보험(005830), 메리츠화재(000060), 삼성화재000810, 코리안리003690, 현대해상001450

은행주
python main.py --stock_code 105560 055550 086790 024110 138930 --rl_method a3c --net lstm --num_steps 10 --learning False --num_epoches 1000 --lr 0.0001 --start_epsilon 0.3 --discount_factor 0.9 --reuse_models --output_name bank_210420 --value_network_name a2c_lstm_value_b_bank --policy_network_name a2c_lstm_policy_b_bank --start_date 20110901 --end_date 20200901

0,0,KB금융,A105560,kospi,221626,2008-10-10,6.41
4,4,신한지주,A055550,kospi,193467,2001-09-10,5.55
7,7,하나금융지주,A086790,kospi,124000,2005-12-12,4.7
8,8,기업은행,A024110,kospi,67588,2003-12-24,4.56
6,6,BNK금융지주,A138930,kospi,22098,2011-03-30,4.26

반도체 장비
python main.py --stock_code 105560 055550 086790 024110 138930 --rl_method a3c --net lstm --num_steps 10 --learning False --num_epoches 1000 --lr 0.0001 --start_epsilon 0.3 --discount_factor 0.9 --reuse_models --output_name semiconduct_210420 --value_network_name a2c_lstm_value_b_semiconduct --policy_network_name a2c_lstm_policy_b_semiconduct --start_date 20110901 --end_date 20200901


,Unnamed: 0,name,code,class,market_cap,reg_day,per
47,47,삼성전자,A005930,kospi,4984768,1975-06-11,21.74
95,95,SK하이닉스,A000660,kospi,1004643,1996-12-26,21.13
32,32,삼성전자우,A005935,kospi,618811,1975-06-11,19.58
85,85,DB하이텍,A000990,kospi,24464,1975-12-12,14.77
96,96,리노공업,A058470,kosdaq,24159,2001-12-18,43.63

건설
python main.py --stock_code 000720 006360 047040 028050 010780 --rl_method a3c --net lstm --num_steps 10 --learning False --num_epoches 1000 --lr 0.0001 --start_epsilon 0.3 --discount_factor 0.9 --reuse_models --output_name construction_210422 --value_network_name a2c_lstm_value_b_construction --policy_network_name a2c_lstm_policy_b_construction --start_date 20110901 --end_date 20200901


,Unnamed: 0,name,code,class,market_cap,reg_day,per
60,60,현대건설,A000720,kospi,50945,1984-12-22,41.67
52,52,GS건설,A006360,kospi,38385,1981-08-03,11.54
45,45,대우건설,A047040,kospi,28096,2001-03-23,9.9
38,38,삼성엔지니어링,A028050,kospi,27244,1996-12-24,11.13
30,30,아이에스동서,A010780,kospi,17856,1986-01-27,14.37