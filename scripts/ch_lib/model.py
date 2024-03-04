# -*- coding: UTF-8 -*-
# handle msg between js and python side
import os
import json
from . import util
from modules import shared


# this is the default root path
root_path = os.getcwd()

# if command line arguement is used to change model folder, 
# then model folder is in absolute path, not based on this root path anymore.
# so to make extension work with those absolute model folder paths, model folder also need to be in absolute path
folders = {
    "ti": os.path.join(root_path, "embeddings"),
    "hyper": os.path.join(root_path, "models", "hypernetworks"),
    "ckp": os.path.join(root_path, "models", "Stable-diffusion"),
    "lora": os.path.join(root_path, "models", "Lora"),
}

exts = (".bin", ".pt", ".safetensors", ".ckpt")
info_ext = ".info"
vae_suffix = ".vae"


# get cusomter model path
def get_custom_model_folder():
    util.printD("Get Custom Model Folder")

    global folders

    if shared.cmd_opts.embeddings_dir and os.path.isdir(shared.cmd_opts.embeddings_dir):
        folders["ti"] = shared.cmd_opts.embeddings_dir

    if shared.cmd_opts.hypernetwork_dir and os.path.isdir(shared.cmd_opts.hypernetwork_dir):
        folders["hyper"] = shared.cmd_opts.hypernetwork_dir

    if shared.cmd_opts.ckpt_dir and os.path.isdir(shared.cmd_opts.ckpt_dir):
        folders["ckp"] = shared.cmd_opts.ckpt_dir

    if shared.cmd_opts.lora_dir and os.path.isdir(shared.cmd_opts.lora_dir):
        folders["lora"] = shared.cmd_opts.lora_dir





# write model info to file
def write_model_info(path, model_info):
    util.printD("Write model info to file: " + path)
    with open(os.path.realpath(path), 'w') as f:
        f.write(json.dumps(model_info, indent=4))


def load_model_info(path):
    # util.printD("Load model info from file: " + path)
    model_info = None
    with open(os.path.realpath(path), 'r') as f:
        try:
            model_info = json.load(f)
        except Exception as e:
            util.printD("Selected file is not json: " + path)
            util.printD(e)
            return
        
    return model_info


# get model file names by model type
# parameter: model_type - string
# return: model name list
def get_model_names_by_type(model_type:str) -> list:
    
    model_folder = folders[model_type]

    # get information from filter
    # only get those model names don't have a civitai model info file
    model_names = []
    for root, dirs, files in os.walk(model_folder, followlinks=True):
        for filename in files:
            item = os.path.join(root, filename)
            # check extension
            base, ext = os.path.splitext(item)
            if ext in exts:
                # find a model
                model_names.append(filename)


    return model_names


# return 2 values: (model_root, model_path)
def get_model_path_by_type_and_name(model_type:str, model_name:str) -> str:
    util.printD("Run get_model_path_by_type_and_name")
    if model_type not in folders.keys():
        util.printD("unknown model_type: " + model_type)
        return
    
    if not model_name:
        util.printD("model name can not be empty")
        return
    
    folder = folders[model_type]

    # model could be in subfolder, need to walk.
    model_root = ""
    model_path = ""
    for root, dirs, files in os.walk(folder, followlinks=True):
        for filename in files:
            if filename == model_name:
                # find model
                model_root = root
                model_path = os.path.join(root, filename)
                return (model_root, model_path)

    return




# get model path by model type and search_term
# parameter: model_type, search_term
# return: model_path
def get_model_path_by_search_term(model_type:str, search_term:str):
    util.printD(f"Search model of {search_term} in {model_type}")
    if model_type not in folders.keys():
        util.printD("unknow model type: " + model_type)
        return
    
    # for lora: search_term = subfolderpath + model name + ext + " " + hash. And it always start with a / even there is no sub folder
    # for ckp: search_term = subfolderpath + model name + ext + " " + hash
    # for ti: search_term = subfolderpath + model name + ext + " " + hash
    # for hyper: search_term = subfolderpath + model name
    has_hash = True
    if model_type == "hyper":
        has_hash = False
    elif search_term.endswith(".pt") or search_term.endswith(".bin") or search_term.endswith(".safetensors") or search_term.endswith(".ckpt"):
        has_hash = False

    # remove hash
    # model name may have multiple spaces
    splited_path = search_term.split()
    model_sub_path = splited_path[0]
    if has_hash and len(splited_path) > 1:
        model_sub_path = ""
        for i in range(0, len(splited_path)-1):
            model_sub_path += splited_path[i] + " "
        
        model_sub_path = model_sub_path.strip()

    if model_sub_path[:1] == "/":
        model_sub_path = model_sub_path[1:]

    model_folder_name = "";
    if model_type == "ti":
        model_folder_name = "embeddings"
    elif model_type == "hyper":
        model_folder_name = "hypernetworks"
    elif model_type == "ckp":
        model_folder_name = "Stable-diffusion"
    else:
        model_folder_name = "Lora"

    # check if model folder is already in search_term
    if model_sub_path.startswith(model_folder_name):
        # this is sd webui v1.8.0+'s search_term
        # need to remove this model_folder_name+"/"or""\\" from model_sub_path
        model_sub_path = model_sub_path[len(model_folder_name):]

        if model_sub_path.startswith("/") or model_sub_path.startswith("\\"):
            model_sub_path = model_sub_path[1:]

    if model_type == "hyper":
        if not model_sub_path.endswith(".pt"):
            model_sub_path = model_sub_path+".pt"

    model_folder = folders[model_type]

    model_path = os.path.join(model_folder, model_sub_path)

    print("model_folder: " + model_folder)
    print("model_sub_path: " + model_sub_path)
    print("model_path: " + model_path)

    if not os.path.isfile(model_path):
        util.printD("Can not find model file: " + model_path)
        return
    
    return model_path

