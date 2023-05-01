# coding: utf-8
# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 2023-04-29

import os
import time
import json
from langchain.text_splitter import CharacterTextSplitter

def get_envs(path=".env") -> dict:
    env_dict = dict()
    with open(path, "r") as env_f:
        for line in env_f.readlines():
            env_dict[line.split("=")[0].strip()] = line.split("=")[1].strip()
    return env_dict

def load_envs(env_dict) -> None:
    for k in env_dict:
        os.environ[k] = env_dict[k]

def get_current_time() -> str:
    return time.strftime('%c')

def get_current_location(location) -> str:
    # TODO(mingzhe)
    return str(location)

def response_parse(response_raw):
    try:
        response_json = json.loads(response_raw)
    except Exception as e:
        print(f"OpenAI Response Parsing Error: {e}")
        return None
    return response_json

# Load Environment Variables in advance
load_envs(get_envs())
