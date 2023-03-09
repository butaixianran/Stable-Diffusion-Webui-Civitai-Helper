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
        "skip_nsfw_preview": False
    },
    "general":{
        "open_url_with_js": True,
        "check_model_version_at_startup": False,
    },
    "tool":{
    },
	"jokker":{
		"min_weight": 1,
		"max_weight": 10
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
def save_from_input(low_memory_sha, max_size_preview, skip_nsfw_preview, open_url_with_js, check_model_version_at_startup, minWeight, maxWeight):
    global data
    data = {
        "model":{
            "low_memory_sha": low_memory_sha,
            "max_size_preview": max_size_preview,
            "skip_nsfw_preview": skip_nsfw_preview
        },
        "general":{
            "open_url_with_js": open_url_with_js,
            "check_model_version_at_startup": check_model_version_at_startup,
        },
        "tool":{
        },
		"jokker":{
			"min_weight": minWeight,
			"max_weight": maxWeight
		}
    }

    output = save()

    if not output:
        output = ""

    return output

# load to output
def load_to_output():
    load()

    low_memory_sha = data["model"]["low_memory_sha"]
    max_size_preview = data["model"]["max_size_preview"]
    skip_nsfw_preview = data["model"]["skip_nsfw_preview"]
    open_url_with_js = data["general"]["open_url_with_js"]
    check_model_version_at_startup = data["general"]["check_model_version_at_startup"]


    return [low_memory_sha, max_size_preview, skip_nsfw_preview, open_url_with_js, check_model_version_at_startup]