class NodeConfig:

    def __init__(self, config_dict):
        self.name = config_dict.get("name", "")
        self.ip = config_dict.get("ip", "")
        self.role = config_dict.get("role", "")
