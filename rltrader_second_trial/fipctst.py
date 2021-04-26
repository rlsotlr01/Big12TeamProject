import fipc

print('종목수:', len(fipc.get_tot_items()))

tsdf = fipc.get_tseries('A000210', count=100)
print(tsdf)

