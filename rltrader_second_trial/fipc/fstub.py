import getopt
import sys
from pickle import dump

from fipc.dsapi import *

FIPC_DEBUG = True
ext = 'ipp'  # file extension name of dummy file for communicating between 32 and 64 bit python

fipsspec = {
    'init_trade': {'fp': init_trade, 'loptstr': ''},
    'buy': {'fp': buy, 'loptstr': 'itcode|quantity|price|ttype'},
    'sell': {'fp': sell, 'loptstr': 'itcode|quantity|price|ttype'},
    'get_portfolio': {'fp': get_portfolio, 'loptstr': ''},
    'get_curp': {'fp': get_curp, 'loptstr': 'itcode'},
    'get_item': {'fp': get_item, 'loptstr': 'itcode'},
    'get_items': {'fp': get_items, 'loptstr': 'bycode'},
    'get_tseries': {'fp': get_tseries, 'loptstr': 'itcode|start|to|count|ctype'}
}


def lopts_eq(optstr):
    popts = optstr.split('|')
    return [o + str('=') for o in popts]


def dashdash_lopts(optstr):
    popts = optstr.split('|')
    return [str('--') + o for o in popts]


# unified fipc broker (entry pointer to call)
if __name__ == '__main__':
    # parse argv and set opts
    func = sys.argv[1]
    loptstr = fipsspec[func]['loptstr']

    if FIPC_DEBUG:
        # redirect to stderr because stdout print() doesn't work
        print(cfg.fupath_pyx32, cfg.fupath_fipcstub, func, ' '.join(sys.argv[2:]), file=sys.stderr)

    try:
        opts, _ = getopt.getopt(sys.argv[2:], '', lopts_eq(loptstr) + [ext + str('=')])
    except getopt.GetoptError as e:
        print(e)

    lopts = dashdash_lopts(loptstr)
    args = {}

    # parsing opts
    for opt, argv in opts:
        for lop in lopts:
            if opt == lop:
                # type conversion except string
                if argv == 'True' or argv == 'False':
                    argv = util.to_bool(argv)

                # try convertions into int
                try:
                    argv = float(argv) if '.' in argv else int(argv)
                except:
                    pass  # string

                # set args
                args[opt[2:]] = argv  # remove '--'
        if opt == '--ipp':
            ippath = argv

    # default or post-proc args per func
    if func == 'get_tseries':
        args['start'] = dt.datetime.strptime(str(args['start']), '%Y%m%d') if 'start' in args.keys() else None
        args['to'] = dt.datetime.strptime(str(args['to']), '%Y%m%d') if 'to' in args.keys() else dt.date.today()
        args['count'] = args.get('count', -1)

    init_trade()
    res = fipsspec[func]['fp'](**args)
    dump(res, open(ippath, 'wb'))
