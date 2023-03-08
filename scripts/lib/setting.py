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
        "low_memory_sha": True,
        "max_size_preview": True,
        "readable_model_info": True,
        "skip_nsfw_preview": False
    },
    "general":{
        "open_url_with_js": False,
        "check_model_version_at_startup": False,
    },
    "tool":{
    }
}



# save setting
def save():
    print("Saving tranlation service setting...")
    # write data into globel trans_setting
    global trans_setting

    

    # to json
    json_data = json.dumps(data)

    #write to file
    try:
        with open(path, 'w') as f:
            f.write(json_data)
    except Exception as e:
        util.printD("Error when writing file:"+path)
        util.printD(str(e))
        return

    util.printD("Setting saved to: " + path)


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