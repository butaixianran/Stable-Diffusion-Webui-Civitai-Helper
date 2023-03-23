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
        "always_display": False,
        "show_btn_on_thumb": True,
    },
    "tool":{
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

    # check for new key
    if "always_display" not in data["general"].keys():
        data["general"]["always_display"] = False

    if "show_btn_on_thumb" not in data["general"].keys():
        data["general"]["show_btn_on_thumb"] = True


    return

# save setting from parameter
def save_from_input(max_size_preview, skip_nsfw_preview, open_url_with_js, always_display, show_btn_on_thumb):
    global data
    data = {
        "model":{
            "max_size_preview": max_size_preview,
            "skip_nsfw_preview": skip_nsfw_preview
        },
        "general":{
            "open_url_with_js": open_url_with_js,
            "always_display": always_display,
            "show_btn_on_thumb": show_btn_on_thumb,
        },
        "tool":{
        }
    }

    output = save()

    if not output:
        output = ""

    return output

