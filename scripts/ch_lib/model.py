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
    "lycoris": os.path.join(root_path, "models", "LyCORIS"),
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

    try:
        # pre-1.5.0
        if shared.cmd_opts.lyco_dir and os.path.isdir(shared.cmd_opts.lyco_dir):
            folders["lycoris"] = shared.cmd_opts.lyco_dir

    except:
        try:
            # sd-webui v1.5.1 added a backcompat option for lyco.
            if shared.cmd_opts.lyco_dir_backcompat and os.path.isdir(shared.cmd_opts.lyco_dir_backcompat):
                folders["lycoris"] = shared.cmd_opts.lyco_dir_backcompat
        except:
            # XXX v1.5.0 has no options for the Lyco dir: it is hardcoded as 'os.path.join(paths.models_path, "LyCORIS")'
            pass


# write model info to file
def write_model_info(path, model_info):
    util.printD(f"Write model info to file: {path}")
    with open(os.path.realpath(path), 'w') as f:
        f.write(json.dumps(model_info, indent=4))


def load_model_info(path):
    # util.printD("Load model info from file: " + path)
    model_info = None
    with open(os.path.realpath(path), 'r') as f:
        try:
            model_info = json.load(f)
        except Exception as e:
            util.printD(f"Selected file is not json: {path}")
            util.printD(e)
            return

    return model_info


# get model file names by model type
# parameter: model_type - string
# return: model name list
def get_model_names_by_type(model_type:str) -> list:

    if model_type == "lora" and folders['lycoris']:
        model_folders = [folders[model_type], folders['lycoris']]
    else:
        model_folders = [folders[model_type]]

    # get information from filter
    # only get those model names don't have a civitai model info file
    model_names = []
    for model_folder in model_folders:
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
        util.printD(f"unknown model_type: {model_type}")
        return

    if not model_name:
        util.printD("model name can not be empty")
        return

    if model_type == "lora" and folders['lycoris']:
        model_folders = [folders[model_type], folders['lycoris']]
    else:
        model_folders = [folders[model_type]]


    # model could be in subfolder, need to walk.
    model_root = ""
    model_path = ""
    for folder in model_folders:
        for root, dirs, files in os.walk(folder, followlinks=True):
            for filename in files:
                if filename == model_name:
                    # find model
                    model_root = root
                    model_path = os.path.join(root, filename)
                    return (model_root, model_path)

    return



