# -*- coding: UTF-8 -*-
# collecting settings to here
import json
import os
import modules.scripts as scripts
from . import util


name = "setting.json"
path = os.path.join(scripts.basedir(), name)

data = {
    "model":{
        "max_size_preview": True,
        "skip_nsfw_preview": False
    },
    "general":{
        "open_url_with_js": True,
    },
    "tool":{
    },
    "jokker":{
        "min_weight": 0,
        "max_weight": 2,
        "lora_configs":{
        }
    }
}



# save setting
# return output msg for log
def save():
    print("Saving setting to: " + path)

    json_data = json.dumps(data, indent=4)

    output = ""

    #write to file
    try:
        with open(path, 'w') as f:
            f.write(json_data)
    except Exception as e:
        util.printD("Error when writing file:"+path)
        output = str(e)
        util.printD(str(e))
        return output

    output = "Setting saved to: " + path
    util.printD(output)

    return output


# load setting to global data
def load():
    # load data into globel data
    global data

    util.printD("Load setting from: " + path)

    if not os.path.isfile(path):
        util.printD("No setting file, use default")
        return

    json_data = None
    with open(path, 'r') as f:
        json_data = json.load(f)

    # check error
    if not json_data:
        util.printD("load setting file failed")
        return

    data = json_data

    return

# save setting from parameter
def save_from_input(max_size_preview, skip_nsfw_preview, open_url_with_js, minWeight, maxWeight):
    global data
    lora_configs = data["jokker"]["lora_configs"]
    data = {
        "model":{
            "max_size_preview": max_size_preview,
            "skip_nsfw_preview": skip_nsfw_preview
        },
        "general":{
            "open_url_with_js": open_url_with_js,
        },
        "tool":{
        },
        "jokker":{
            "min_weight": minWeight,
            "max_weight": maxWeight,
            "lora_configs": lora_configs
        }
    }

    output = save()

    if not output:
        output = ""

    return output

# load to output
def load_to_output():
    load()

    max_size_preview = data["model"]["max_size_preview"]
    skip_nsfw_preview = data["model"]["skip_nsfw_preview"]
    open_url_with_js = data["general"]["open_url_with_js"]


    return [max_size_preview, skip_nsfw_preview, open_url_with_js]