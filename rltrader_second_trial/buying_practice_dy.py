import fipc



fipc.get_portfolio()
fipc.get_tot_items('A005930')
tsdf = fipc.get_tseries('A005930', count=100)
print(tsdf)