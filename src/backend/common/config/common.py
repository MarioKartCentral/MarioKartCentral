import os
from typing import Type

import msgspec


def load_config[T](file_name: str, type: Type[T]) -> T:
    config_dir = os.environ["CONFIG_PATH"]
    with open(os.path.join(config_dir, file_name), 'rb') as r:
        return msgspec.json.decode(r.read(), type=type)