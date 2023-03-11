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
    lora_configs = setting.data["jokker"]["lora_configs"]
    util.printD("Start load_lora_configs")

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
