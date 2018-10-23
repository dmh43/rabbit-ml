from abc import abstractmethod, ABC

import getopt
import sys

from dotenv import dotenv_values, find_dotenv
from pyrsistent import m
import pydash as _

# format for `args`:
# args =  [{'name': 'batch_size'                 , 'for': 'train_params', 'type': int},
#          {'name': 'dropout_keep_prob'          , 'for': 'train_params', 'type': float},
#          {'name': 'train_size'                 , 'for': 'train_params', 'type': int},
#          {'name': 'num_epochs'                 , 'for': 'train_params', 'type': int},
#          {'name': 'ablation'                   , 'for': 'model_params', 'type': lambda string: string.split(',')},
#          {'name': 'document_encoder_lstm_size' , 'for': 'model_params', 'type': int},
#          {'name': 'embed_len'                  , 'for': 'model_params', 'type': int},
#          {'name': 'local_encoder_lstm_size'    , 'for': 'model_params', 'type': int},
#          {'name': 'num_candidates'             , 'for': 'model_params', 'type': int},
#          {'name': 'num_lstm_layers'            , 'for': 'model_params', 'type': int},
#          {'name': 'word_embed_len'             , 'for': 'model_params', 'type': int},
#          {'name': 'word_embedding_set'         , 'for': 'model_params', 'type': str},
#          {'name': 'adaptive_softmax_cutoffs'   , 'for': 'model_params', 'type': lambda string: [int(cutoff) for cutoff in string.split(',')]},
#          {'name': 'comments'                   , 'for': 'run_params', 'type': str},
#          {'name': 'load_model'                 , 'for': 'run_params', 'type': 'flag'},
#          {'name': 'use_adaptive_softmax'       , 'for': 'run_params', 'type': 'flag'},
#          {'name': 'use_hardcoded_cutoffs'      , 'for': 'run_params', 'type': 'flag'}]

def run():
  def _run_wrapper(func):
    import ipdb
    import traceback
    import sys
    try:
      func()
    except: # pylint: disable=bare-except
      extype, value, tb = sys.exc_info()
      traceback.print_exc()
      ipdb.post_mortem(tb)

class Rabbit(ABC):
  def __init__(self, args, env_path=None):
    if env_path is None:
      env = dotenv_values(find_dotenv())
    else:
      env = dotenv_values(env_path)
    args = self._get_cli_args(args)
    flags = [_.head(arg) for arg in args]
    self.train_params, self.run_params, self.model_params = m(), m(), m()
    self.paths = m(**{var[0].lower()[:-5]: var[1] for var in env.items() if '_PATH' in var[0]})
    for arg in args:
      name = arg['name']
      pair = _.find(args, lambda pair: name in pair[0])
      if pair:
        if arg['type'] == 'flag':
          val = '--' + arg['name'] in flags
        else:
          val = arg['type'](pair[1])
      else:
        val = arg['default']
      if arg['for'] == 'path':
        self.paths = self.paths.set(name, val)
      elif arg['for'] == 'model_params':
        self.model_params = self.model_params.set(name, val)
      elif arg['for'] == 'train_params':
        self.train_params = self.train_params.set(name, val)
      elif arg['for'] == 'run_params':
        self.run_params = self.run_params.set(name, val)
      else:
        raise ValueError('`args_with_values` contains unsupported param group ' + arg['for'])

  def _get_cli_args(self, args):
    args_with_values = filter(lambda arg: arg['type'] != 'flag', args)
    flag_argnames = filter(lambda arg: arg['type'] == 'flag', args)
    return getopt.getopt(_.tail(sys.argv),
                         '',
                         flag_argnames + [arg['name'] + '=' for arg in args_with_values])[0]

  @abstractmethod
  def run(self):
    pass
