# set python32 path
fupath_pyx32 = 'C:/Users/JungJaeYong/anaconda3/envs/py36_32/python.exe'

# set path of fipc stub which is cmd line parser
fupath_fipcstub = 'F:/TeamStockProject/rltrader_second_trial/fipc/fstub.py'

# temp dir used fake ipc
temp_dir = 'F:/stock_log'

# your account
acc = '33505561310'

# trading cfg
total_amount_per_day = 3000000
amount_per_trading = 500000
max_cnt_trading = int(total_amount_per_day / amount_per_trading)
tick = 10  # used in get_tseries when ctype='m'
