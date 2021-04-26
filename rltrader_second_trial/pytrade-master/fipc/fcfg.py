# set python32 path
fupath_pyx32 = 'C:\\Python36x32\\python.exe'

# set path of fipc stub which is cmd line parser
fupath_fipcstub = 'E:\\gdrv\\sytra\\fipc\\fstub.py'

# temp dir used fake ipc
temp_dir = 'C:\\Temp\\sytrap'

# your account
acc = ''

# trading cfg
total_amount_per_day = 3000000
amount_per_trading = 500000
max_cnt_trading = int(total_amount_per_day / amount_per_trading)
tick = 10  # used in get_tseries when ctype='m'
