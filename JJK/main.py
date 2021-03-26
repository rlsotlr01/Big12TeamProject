# main program
# main.py

import stock_kind as sk
import collect_day.collect_day as cd
import real_time.real_time_price as rt


def start_collect_stock_kind():
    collect_stock_kind = sk.StockKind()
    return collect_stock_kind.start_collect()


def start_collect_day(codes):
    collect_stock_day = cd.DayCollect()
    collect_stock_day.start_get_days_data(codes)


def start_collect_real_time():
    collect_real_time = rt.RealTimeCollect()
    collect_real_time.start_collect_real_time_data()


codes = start_collect_stock_kind()
start_collect_day(codes)
# start_collect_real_time()
