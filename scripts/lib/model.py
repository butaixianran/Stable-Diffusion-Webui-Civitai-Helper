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



# get cusomter model path
def get_custom_model_folder():
    global folders

    if shared.cmd_opts.embeddings_dir and os.path.isdir(shared.cmd_opts.embeddings_dir):
        folders["ti"] = shared.cmd_opts.embeddings_dir

    if shared.cmd_opts.hypernetwork_dir and os.path.isdir(shared.cmd_opts.hypernetwork_dir):
        folders["hyper"] = shared.cmd_opts.hypernetwork_dir

    if shared.cmd_opts.ckpt_dir and os.path.isdir(shared.cmd_opts.ckpt_dir):
        folders["ckp"] = shared.cmd_opts.ckpt_dir

    if shared.cmd_opts.lora_dir and os.path.isdir(shared.cmd_opts.lora_dir):
        folders["lora"] = shared.cmd_opts.lora_dir

get_custom_model_folder()



# write model info to file
def write_model_info(path, model_info):
    util.printD("Write model info to file: " + path)
    with open(path, 'w') as f:
        f.write(json.dumps(model_info, indent=4))


def load_model_info(path):
    util.printD("Load model info from file: " + path)
    model_info = None
    with open(path, 'r') as f:
        try:
            model_info = json.load(f)
        except Exception as e:
            util.printD("Selected file is not json: " + path)
            util.printD(e)
            return
        
    return model_info

