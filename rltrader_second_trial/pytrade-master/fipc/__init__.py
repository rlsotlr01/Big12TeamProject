import datetime as dt

from fipc import fakeipc

fi = fakeipc.SytrapFakeIpc()
debug = False  # default


def get_tot_items(bycode=True):
    return fi.call('get_items', bycode=bycode)


def get_item(itcode):
    return fi.call('get_item', itcode=itcode)


def get_portfolio():
    return fi.call('get_portfolio')


def get_tseries(itcode, count=-1, ctype='D', start=(dt.date.today() + dt.timedelta(days=-1)).strftime('%Y%m%d'),
                to=dt.date.today().strftime('%Y%m%d')):
    return fi.call('get_tseries', itcode=itcode, start=start, to=to, count=count, ctype=ctype)


def get_curp(itcode):
    return fi.call('get_curp', itcode=itcode)


def buy(itcode, quantity, price, ttype='normal'):
    return fi.call('buy', itcode=itcode, quantity=quantity, price=price, ttype=ttype)


def sell(itcode, quantity, price, ttype='normal'):
    return fi.call('sell', itcode=itcode, qunatity=quantity, price=price, ttype=ttype)
