# -*- coding: UTF-8 -*-
# handle msg between js and python side
import os
import json
import re
import requests
from . import util
from . import model
from . import setting

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



def get_model_info_by_id(id:str) -> dict:
    util.printD("Request model info from civitai")

    if not id:
        util.printD("id is empty")
        return

    r = requests.get(url_dict["modelId"]+str(id))
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


def get_version_info_by_version_id(id:str) -> dict:
    util.printD("Request version info from civitai")

    if not id:
        util.printD("id is empty")
        return

    r = requests.get(url_dict["modelVersionId"]+id)
    if not r.ok:
        if r.status_code == 404:
            # this is not a civitai model
            util.printD("Civitai does not have this model version")
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


def get_version_info_by_model_id(id:str) -> dict:

    model_info = get_model_info_by_id(id)
    if not model_info:
        util.printD(f"Failed to get model info by id: {id}")
        return
    
    # check content to get version id
    if "modelVersions" not in model_info.keys():
        util.printD("There is no modelVersions in this model_info")
        return
    
    if not model_info["modelVersions"]:
        util.printD("modelVersions is None")
        return
    
    if len(model_info["modelVersions"])==0:
        util.printD("modelVersions is Empty")
        return
    
    def_version = model_info["modelVersions"][0]
    if not def_version:
        util.printD("default version is None")
        return
    
    if "id" not in def_version.keys():
        util.printD("default version has no id")
        return
    
    version_id = def_version["id"]
    
    if not version_id:
        util.printD("default version's id is None")
        return

    # get version info
    version_info = get_version_info_by_version_id(str(version_id))
    if not version_info:
        util.printD(f"Failed to get version info by version_id: {version_id}")
        return

    return version_info




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





# get model file names by model type
# parameter: model_type - string
# parameter: filter - dict, which kind of model you need
# return: model name list
def get_model_names_by_type_and_filter(model_type:str, filter:dict) -> list:
    
    model_folder = model.folders[model_type]

    # set filter
    # only get models don't have a civitai info file
    no_info_only = False
    empty_info_only = False

    if filter:
        if "no_info_only" in filter.keys():
            no_info_only = filter["no_info_only"]
        if "empty_info_only" in filter.keys():
            empty_info_only = filter["empty_info_only"]



    # get information from filter
    # only get those model names don't have a civitai model info file
    model_names = []
    for root, dirs, files in os.walk(model_folder):
        for filename in files:
            item = os.path.join(root, filename)
            # check extension
            base, ext = os.path.splitext(item)
            if ext in model.exts:
                # find a model

                # check filter
                if no_info_only:
                    # check model info file
                    info_file = base + suffix + model.info_ext
                    if os.path.isfile(info_file):
                        continue

                if empty_info_only:
                    # check model info file
                    info_file = base + suffix + model.info_ext
                    if os.path.isfile(info_file):
                        # load model info
                        model_info = model.load_model_info(info_file)
                        # check content
                        if model_info:
                            if "id" in model_info.keys():
                                # find a non-empty model info file
                                continue

                model_names.append(filename)


    return model_names

def get_model_names_by_input(model_type, empty_info_only):
    return get_model_names_by_type_and_filter(model_type, {"empty_info_only":empty_info_only})
    

# get id from url
def get_model_id_from_url(url:str) -> str:
    util.printD("Run get_model_id_from_url")
    id = ""

    if not url:
        util.printD("url or model id can not be empty")
        return ""

    if url.isnumeric():
        # is already an id
        id = url
        return ""
    
    s = url.split("/")
    if len(s) < 2:
        util.printD("url is not valid")
        return ""
    
    if s[-2].isnumeric():
        id  = s[-2]
    elif s[-1].isnumeric():
        id  = s[-1]
    else:
        util.printD("There is no model id in this url")
        return ""
    
    return id


# get preview image by model path
# image will be saved to file, so no return
def get_preview_image_by_model_path(model_path:str, max_size_preview, skip_nsfw_preview) -> str:
    if not model_path:
        util.printD("model_path is empty")
        return

    if not os.path.isfile(model_path):
        util.printD("model_path is not a file")
        return

    base, ext = os.path.splitext(model_path)
    first_preview = base+".png"
    sec_preview = base+".preview.png"
    info_file = base + suffix + model.info_ext

    # check preview image
    if not os.path.isfile(sec_preview):
        # need to download preview image
        util.printD("Checking preview image for model: " + model_path)
        # load model_info file
        if os.path.isfile(info_file):
            model_info = model.load_model_info(info_file)
            if not model_info:
                util.printD("Model Info is empty")
                return

            if "images" in model_info.keys():
                if model_info["images"]:
                    for img_dict in model_info["images"]:
                        if "nsfw" in img_dict.keys():
                            if img_dict["nsfw"]:
                                util.printD("This image is NSFW")
                                if skip_nsfw_preview:
                                    util.printD("Skip NSFW image")
                                    continue
                        
                        if "url" in img_dict.keys():
                            img_url = img_dict["url"]
                            if max_size_preview:
                                # use max width
                                if "width" in img_dict.keys():
                                    if img_dict["width"]:
                                        img_url = get_full_size_image_url(img_url, img_dict["width"])

                            util.download_file(img_url, sec_preview)
                            # we only need 1 preview image
                            break

