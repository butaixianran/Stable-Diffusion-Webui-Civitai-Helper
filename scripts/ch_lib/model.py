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
def get_model_path_by_search_term(model_type, search_term):
    util.printD(f"Search model of {search_term} in {model_type}")
    if model_type not in folders.keys():
        util.printD("unknow model type: " + model_type)
        return
    
    # for lora: search_term = subfolderpath + model name + ext + " " + hash. And it always start with a / even there is no sub folder
    # for ckp: search_term = subfolderpath + model name + ext + " " + hash
    # for ti: search_term = subfolderpath + model name + ext + " " + hash
    # for hyper: search_term = subfolderpath + model name



    model_sub_path = search_term.split()[0]
    if model_sub_path[:1] == "/":
        model_sub_path = model_sub_path[1:]

    if model_type == "hyper":
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

