# -*- coding: UTF-8 -*-
# handle msg between js and python side
import os
from . import util
from . import model
from . import civitai
from . import setting


# scan model to generate SHA256, then use this SHA256 to get model info from civitai
# return output msg
def scan_model(low_memory_sha, max_size_preview, skip_nsfw_preview):
    util.printD("Start scan_model")
    lora_configs = setting.data["jokker"]["lora_configs"]
    default_lora_config = {
        "weight": (setting.data["jokker"]["min_weight"]+setting.data["jokker"]["max_weight"])/2,
        "prompt": [],
        "weight_active": True,
        "prompt_active": True
    }

    output = ""
    model_count = 0
    image_count = 0
    # scan_log = ""
    for model_type, model_folder in model.folders.items():
        util.printD("Scanning path: " + model_folder)
        for root, dirs, files in os.walk(model_folder):
            for filename in files:
                # check ext
                item = os.path.join(root, filename)
                base, ext = os.path.splitext(item)
                if ext in model.exts:
                    # find a model
                    # get info file
                    info_file = base + civitai.suffix + model.info_ext
                    # check info file
                    if not os.path.isfile(info_file):
                        util.printD("Creating model info for: " + filename)
                        # get model's sha256
                        hash = util.gen_file_sha256(item, low_memory_sha)

                        if not hash:
                            output = "failed generating SHA256 for model:" + filename
                            util.printD(output)
                            return output
                        
                        # use this sha256 to get model info from civitai
                        model_info = civitai.get_model_info_by_hash(hash)
                        if model_info is None:
                            output = "Failed to get model_info"
                            util.printD(output)
                            return output+", check console log for detail"
                        
                        # write model info to file
                        model.write_model_info(info_file, model_info)
                        util.printD("---------- check if lora config is present")
                        modelname = os.path.basename(base)
                        if modelname not in lora_configs:
                            util.printD("---------- it's not, saving lora config")
                            lora_configs[modelname] = default_lora_config.copy()
                            if "trainedWords" in model_info:
                                lora_configs[modelname]["prompt"] = model_info["trainedWords"]

                    # set model_count
                    model_count = model_count+1

                    # check preview image
                    civitai.get_preview_image_by_model_path(item, max_size_preview, skip_nsfw_preview)
                    image_count = image_count+1

    setting.data["jokker"]["lora_configs"] = lora_configs
    # scan_log = "Done"

    output = f"Done. Scanned {model_count} models, checked {image_count} images"

    util.printD(output)

    return output



# Get model info by model type, name and url
# output is log info to display on markdown component
def get_model_info_by_id(model_type, model_name, model_url_or_id, max_size_preview, skip_nsfw_preview):
    output = ""
    # parse model id
    model_id = civitai.get_model_id_from_url(model_url_or_id)
    if not model_id:
        output = "failed to parse model id from url: " + model_url_or_id
        util.printD(output)
        return output

    # get model file path
    # model could be in subfolder
    result = model.get_model_path_by_type_and_name(model_type, model_name)
    if not result:
        output = "failed to get model file path"
        util.printD(output)
        return output
    
    model_root, model_path = result
    if not model_path:
        output = "model path is empty"
        util.printD(output)
        return output
    
    # get info file path
    base, ext = os.path.splitext(model_path)
    info_file = base + civitai.suffix + model.info_ext

    # get model info    
    #we call it model_info, but in civitai, it is actually version info
    model_info = civitai.get_version_info_by_model_id(model_id)

    if not model_info:
        output = "failed to get model info from url: " + model_url_or_id
        util.printD(output)
        return output
    
    # write model info to file
    model.write_model_info(info_file, model_info)

    util.printD("Saved model info to: "+ info_file)

    # check preview image
    civitai.get_preview_image_by_model_path(model_path, max_size_preview, skip_nsfw_preview)

    output = "Model Info saved to: " + info_file
    return output