from typing import Callable, Any

def list_arg(cast_elem: Callable[[str], Any]):
  return lambda cli_string: [cast_elem(elem) for elem in cli_string.split(',')]

def optional_arg(cast_elem: Callable[[str], Any]):
  return lambda cli_string: cast_elem(cli_string) if cli_string is not None else None
