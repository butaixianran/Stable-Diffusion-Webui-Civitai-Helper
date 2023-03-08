# -*- coding: UTF-8 -*-
# handle msg between js and python side
import os
import json
import re
import requests
from . import util
from . import model


suffix = ".civitai"

url_dict = {
    "modelPage":"https://civitai.com/models/",
    "modelId": "https://civitai.com/api/v1/models/",
    "modelVersionId": "https://civitai.com/api/v1/model-versions/",
    "hash": "https://civitai.com/api/v1/model-versions/by-hash/"
}

# get image with full size
# width is in number, not string
# return: url str
def get_full_size_image_url(image_url, width):
    return re.sub('/width=\d+/', '/width=' + str(width) + '/', image_url)


# use this sha256 to get model info from civitai
# return: model info dict
def get_model_info_by_hash(hash:str):
    util.printD("Request model info from civitai")

    if not hash:
        util.printD("hash is empty")
        return

    r = requests.get(url_dict["hash"]+hash)
    if not r.ok:
        if r.status_code == 404:
            # this is not a civitai model
            util.printD("Civitai does not have this model")
            return {}
        else:
            util.printD("Get error code: " + str(r.status_code))
            util.printD(r.text)
            return

    # try to get content
    content = None
    try:
        content = r.json()
    except Exception as e:
        util.printD("Parse response json failed")
        util.printD(str(e))
        util.printD("response:")
        util.printD(r.text)
        return
    
    if not content:
        util.printD("error, content from civitai is None")
        return
    
    return content



# get model info file's content by model type and search_term
# parameter: model_type, search_term
# return: model_info
def load_model_info_by_search_term(model_type, search_term):
    util.printD(f"Load model info of {search_term} in {model_type}")
    if model_type not in model.folders.keys():
        util.printD("unknow model type: " + model_type)
        return
    
    # search_term = subfolderpath + model name + ext. And it always start with a / even there is no sub folder
    base, ext = os.path.splitext(search_term)
    model_info_base = base
    if base[:1] == "/":
        model_info_base = base[1:]

    model_folder = model.folders[model_type]
    model_info_filename = model_info_base + suffix + model.info_ext
    model_info_filepath = os.path.join(model_folder, model_info_filename)

    if not os.path.isfile(model_info_filepath):
        util.printD("Can not find model info file: " + model_info_filepath)
        return
    
    return model.load_model_info(model_info_filepath)