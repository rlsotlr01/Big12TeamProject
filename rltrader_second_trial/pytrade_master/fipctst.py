from rltrader_second_trial import fipc
import pandas
# print('종목수:', len(fipc.get_tot_items()))
tsdf = fipc.get_cur_price()
print(tsdf)
print()
port = fipc.get_portfolio()
print(port)
print()
tsdf = fipc.get_curp('A005930')
print(tsdf + '\n')
tsdf = fipc.buy('A005930', 1, tsdf, ttype='normal')
print(tsdf + '\n')

