import getopt
import sys

from pyrsistent import m
import pydash as _

from .arg_parsers import *

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

def get_cli_args(args):
  args_with_values = list(filter(lambda arg: arg['type'] != 'flag', args))
  flag_argnames = [arg['name'] for arg in filter(lambda arg: arg['type'] == 'flag', args)]
  cli_args = getopt.getopt(_.tail(sys.argv),
                           '',
                           flag_argnames + [arg['name'] + '=' for arg in args_with_values])[0]
  flags = [_.head(arg) for arg in cli_args]
  train_params, run_params, model_params = m(), m(), m()
  paths = m()
  for arg in args:
    name = arg['name']
    pair = _.find(cli_args, lambda pair: name in pair[0])
    if pair:
      if arg['type'] == 'flag':
        val = '--' + arg['name'] in flags
      else:
        val = arg['type'](pair[1])
    else:
      val = arg['default']
    if arg['for'] == 'path':
      paths = paths.set(name, val)
    elif arg['for'] == 'model_params':
      model_params = model_params.set(name, val)
    elif arg['for'] == 'train_params':
      train_params = train_params.set(name, val)
    elif arg['for'] == 'run_params':
      run_params = run_params.set(name, val)
    else:
      raise ValueError('`args_with_values` contains unsupported param group ' + arg['for'])

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
