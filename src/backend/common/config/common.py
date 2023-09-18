import os
from typing import Type, TypeVar

import msgspec


T = TypeVar('T')

def load_config(file_name: str, type: Type[T]) -> T:
    config_dir = os.environ["CONFIG_PATH"]
    with open(os.path.join(config_dir, file_name), 'rb') as r:
        return msgspec.json.decode(r.read(), type=type)