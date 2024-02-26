import json
import os.path
import pathlib

__data__ = None
__working_dir__ = pathlib.Path(__file__).parent.__str__()
__data_file__ = os.path.join(__working_dir__, "private-data", "key.json")


class ApiKeys:
    def __init__(self):
        global __data_file__
        self.GEMINI_KEY: str = None
        self.GPT_KEY: str = None
        with open(__data_file__, "rb") as fs:
            json_text = fs.read().decode("utf8")
            data = json.loads(json_text)
            self.GEMINI_KEY = data["gemini_key"]
            self.GPT_KEY = data["gpt_key"]

api_keys = ApiKeys()