from contextlib import redirect_stdout

from tabulate import tabulate

class Logger():
  def __init__(self, fh):
    self.status = print
    self.report = lambda *args: print('|'.join([str(arg) for arg in args]))
    self.fh = fh

  def __call__(self, *args):
    with redirect_stdout(self.fh):
      self.report(*args)
    self.report(*args)

  def table(self, obj, name=''):
    print('-----' + name + '-----')
    keys = sorted(list(obj.keys()))
    vals = list(zip(*[obj[key] for key in keys]))
    print(tabulate(vals, headers=keys, tablefmt='orgtbl'))
    print('----------------')
