import os
import random
import time

import numpy as np


def to_date_str(dtime):
    return dtime.strftime('%Y%m%d')


def to_str_ttype(ttype):
    strtype = 'not yet determined'
    if ttype == 53:  # '5' kosdaq
        strtype = 'kosdaq'
    elif ttype == 49:  # '1' kospi
        strtype = 'kospi'
    return strtype


def to_str_ttag(ttag):
    strtype = 'not yet determined'
    if ttag == 49:  # '0' 정상
        strtype = 'normal'
    elif ttag == 50:  # 주의
        strtype = 'caution'
    return strtype


def to_bool(s):
    return s.upper() == "TRUE"


def sav_tseries(ts, fpath):
    ts.to_csv(fpath)


def sleep_time(to, unit):
    utmul = 0
    if unit == 'm':
        utmul = 60  # x 60 sec
    time.sleep(random.randint(1, to) * utmul)


def wait_by(hour):
    while True:
        h = int(time.strftime('%H'))
        if h >= hour:
            break
        sleep_time(10, 'm')


def wait_for_market_opening():
    wait_by(hour=9)


def is_closed_market(before=0):
    hour = int(time.strftime('%H'))
    if hour >= 16 - before:
        return True
    return False


def is_between(start, end):
    hour = int(time.strftime('%H'))
    if hour >= start and hour < end:
        return True
    return False


def mkdir(mydir):
    if not os.path.isdir(mydir):
        os.makedirs(mydir)
    return mydir


def get_it_files(dirpath, fromit=None, isfile=True):
    fs = []
    for f in os.listdir(dirpath):
        if isfile:
            if os.path.isfile(os.path.join(dirpath, f)):
                fs.append(f)
        else:
            fs.append(f)
    try:
        idx = fs.index(fromit)
    except ValueError:
        idx = 0
    return fs[idx:]


def calc_rate(base, compared):
    r = 0
    if base != 0:
        r = (compared - base) / base
    return r


def select_one_ramdomly(itpath, isfile=True):
    its = get_it_files(itpath, isfile=isfile)
    return its[np.random.randint(0, len(its))]


if __name__ == '__main__':
    print(to_bool("True"))
    mkdir('dat\\A1234')
