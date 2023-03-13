# -*- coding: UTF-8 -*-
# handle msg between js and python side
import os
import json
import requests
import webbrowser
from . import util
from . import model
from . import civitai
from . import msg_handler
from . import setting




# get civitai's model url and open it in browser
# parameter: model_type, search_term
# output: python msg - will be sent to hidden textbox then picked by js side
def load_lora_configs(msg):
    util.printD("Start load_lora_configs")
    
    lora_configs = setting.data["jokker"]["lora_configs"]

    output = ""


    # msg content for js
    content = {
        "lora_configs":""
    }

    util.printD(lora_configs)
    util.printD("Send lora config to js")
    content["lora_configs"] = json.dumps(lora_configs, separators=(',', ':'))
    output = msg_handler.build_py_msg("load_lora_configs", content)

    util.printD("End load_lora_configs")
    return output

def save_lora_configs(msg):
    util.printD("Start save_lora_configs")

    lora_configs = setting.data["jokker"]["lora_configs"]

    result = msg_handler.parse_js_msg(msg)
    if not result:
        util.printD("Parsing js ms failed")
        return

    action, model_type, search_term, prompt, neg_prompt = result

    lora_values = prompt.split(";")
    weightValue = lora_values[0]
    promptValue = lora_values[1]
    weightActive = lora_values[2]
    promptActive = lora_values[3]

    if search_term not in lora_configs:
        lora_configs[search_term] = {}

    lora_configs[search_term]["weight"] = float(weightValue)
    lora_configs[search_term]["prompt"] = promptValue
    lora_configs[search_term]["weight_active"] = (weightActive == 'true')
    lora_configs[search_term]["prompt_active"] = (promptActive == 'true')

    setting.save()
    util.printD("End save_lora_configs")