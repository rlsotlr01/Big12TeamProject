import os
import subprocess
import uuid
from pickle import load

from fipc import fcfg as cfg


class SytrapFakeIpc:
    ext = 'ipp'  # semi (ip)c using (p)ickle

    def __init__(self):
        self.ipp = None
        self.precall = None
        self.func = None
        pass

    def call(self, func, **kwargs):

        if self.precall is not None:
            self.precall()

        self.func = func
        args_str = ''
        for key in kwargs.keys():
            if len(str(key)) == 1:
                opt_sym = '-'
            else:
                opt_sym = '--'
            args_str += opt_sym + str(key) + ' ' + str(kwargs[key]) + ' '
        args_str += '--ipp ' + os.path.join(cfg.temp_dir, self.make_ipp())
        fupath = cfg.fupath_pyx32 + ' ' + cfg.fupath_fipcstub + ' ' + func + ' ' + args_str
        proc = subprocess.Popen(fupath,
                                shell=True,
                                stdout=subprocess.PIPE,
                                bufsize=-1)
        proc.wait()
        idp = self.load_ipp()
        return idp

    def make_ipp(self):
        self.ipp = str(uuid.uuid4()) + '.ipp'
        return self.ipp

    def load_ipp(self):
        try:
            with open(os.path.join(cfg.temp_dir, self.ipp), 'rb') as f:
                idump = load(f)
                return idump
        except:
            print('error101 - maybe connections with dashin servers', self.func)

    def set_precall(self, precall):
        self.precall = precall
