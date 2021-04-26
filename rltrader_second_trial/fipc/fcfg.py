# set python32 path
fupath_pyx32 = 'E:/big12/dev-rl/anaconda3/envs/py36_32/python.exe' # 가상환경 주소

# set path of fipc stub which is cmd line parser
fupath_fipcstub = 'C:/Users/tj2/PycharmProjects/Big12TeamProject/rltrader_second_trial/fipc/fstub.py'

# temp dir used fake ipc
temp_dir = 'C:\\Temp\\sytrap'

# your account
acc = '355-055403-10' # 각자의 모의 계좌번호 입력 (DY)

# trading cfg
total_amount_per_day = 3000000
amount_per_trading = 500000
max_cnt_trading = int(total_amount_per_day / amount_per_trading)
tick = 10  # used in get_tseries when ctype='m'
