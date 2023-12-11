class TalosConfig:

    def __init__(self, config_dict):
        self.dir_generated_configuration = config_dict.get(
            "dir_generated_configuration", "")
        self.path_patch_all = config_dict.get("path_patch_all", "")
        self.path_patch_controlplane = config_dict.get(
            "path_patch_controlplane", "")
        self.path_patch_worker = config_dict.get(
            "path_patch_worker", "")
