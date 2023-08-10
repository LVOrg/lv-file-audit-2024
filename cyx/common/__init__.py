import os.path
import pathlib

import cy_kit
config = cy_kit.yaml_config(os.path.join(
    pathlib.Path(__file__).parent.parent.parent.__str__(),"config.yml"
))
"""
All configs of File-Service was store here
"""
config_path = os.path.join(pathlib.Path(__file__).parent.parent.parent.__str__(),"config.yml")
"""
Path to location of config.yml
"""