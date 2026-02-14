from pathlib import Path


class CiliumConfig:

    def __init__(self, config_dict):
        self.path_values = Path(config_dict.get("path_values", ""))
