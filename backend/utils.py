# coding: utf-8
# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 2023-04-29

import os
import time
import json
import task
from tqdm import tqdm
from langchain.text_splitter import TokenTextSplitter

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
        print(f"OpenAI Response Parsing Error: {e} RAW response: {response_raw}")
        return response_raw
    return response_json

def recursive_summary(llm, raw_text, question, text_length=800, chunk_size=800):
    while llm.get_num_tokens(raw_text) > text_length:
        text_splitter = TokenTextSplitter(chunk_size=chunk_size, chunk_overlap=100)
        texts = text_splitter.split_text(raw_text)
    
        summarization_list = list()
        for text in tqdm(texts, desc="Recursive Summary"):
            summarization = task.SummaryTask("summary", {
                "text": text,
                "question": question,
                "fast_model": True
            }).execute()
            summarization_list += [summarization]
        raw_text = " ".join(summarization_list)
    return raw_text

def get_history_str(msg_list):
    history = list()
    for msg in msg_list:
        history += [f"{msg.type}: {msg.content}"]
    return str(history)

def kuibu_validation(raw_response):
    try:
        step_list = response_parse(raw_response)
        for i in step_list:
            print(f"step_description: {i['step_description']}, step_result_needed: {i['step_result_needed']}")
        return step_list
    except Exception as e:
        print(e)
        return None
    
def send_message(message, style="system", socket_config=None):
    if socket_config:
        sio, sid = socket_config
        sio.emit('message', {'content': message, "style": style}, room=sid)
    print(f"[{style}] {message}")

# Load Environment Variables in advance
load_envs(get_envs())
