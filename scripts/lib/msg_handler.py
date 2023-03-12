# -*- coding: UTF-8 -*-
# handle msg between js and python side
import json
from . import util

# action list
js_actions = ("save_lora_configs","open_url", "add_trigger_words", "use_preview_prompt")
py_actions = ("load_lora_configs","open_url", "scan_log", "model_new_version")


# handle request from javascript
# parameter: msg - msg from js as string in a hidden textbox
# return: (action, model_type, search_term, prompt, neg_prompt)
def parse_js_msg(msg):
    util.printD("Start parse js msg")
    msg_dict = json.loads(msg)

    if "action" not in msg_dict.keys():
        util.printD("Can not find action from js request")
        return
    
    if "model_type" not in msg_dict.keys():
        util.printD("Can not find model type from js request")
        return
    
    if "search_term" not in msg_dict.keys():
        util.printD("Can not find search_term from js request")
        return
    
    if "prompt" not in msg_dict.keys():
        util.printD("Can not find prompt from js request")
        return
    
    if "neg_prompt" not in msg_dict.keys():
        util.printD("Can not find neg_prompt from js request")
        return
    
    action = msg_dict["action"]
    model_type = msg_dict["model_type"]
    search_term = msg_dict["search_term"]
    prompt = msg_dict["prompt"]
    neg_prompt = msg_dict["neg_prompt"]

    if not action:
        util.printD("Action from js request is None")
        return

    if not model_type:
        util.printD("model_type from js request is None")
        return
    
    if not search_term:
        util.printD("search_term from js request is None")
        return
    

    if action not in js_actions:
        util.printD("Unknow action: " + action)
        return

    util.printD("End parse js msg")

    return (action, model_type, search_term, prompt, neg_prompt)


# build python side msg for sending to js
# parameter: content dict
# return: msg as string, to fill into a hidden textbox
def build_py_msg(action:str, content:dict):
    util.printD("Start build_msg")
    if not content:
        util.printD("Content is None")
        return
    
    if not action:
        util.printD("Action is None")
        return

    if action not in py_actions:
        util.printD("Unknow action: " + action)
        return

    msg = {
        "action" : action,
        "content": content
    }


    util.printD("End build_msg")
    return json.dumps(msg)