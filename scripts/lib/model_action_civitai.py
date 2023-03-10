# -*- coding: UTF-8 -*-
# handle msg between js and python side
import os
from . import util
from . import model
from . import civitai
from markdownify import markdownify as md


# scan model to generate SHA256, then use this SHA256 to get model info from civitai
# return output msg
def scan_model(max_size_preview, skip_nsfw_preview):
    util.printD("Start scan_model")

    output = ""
    model_count = 0
    image_count = 0
    # scan_log = ""
    for model_type, model_folder in model.folders.items():
        util.printD("Scanning path: " + model_folder)
        for root, dirs, files in os.walk(model_folder, followlinks=True):
            for filename in files:
                # check ext
                item = os.path.join(root, filename)
                base, ext = os.path.splitext(item)
                if ext in model.exts:
                    # find a model
                    # get info file
                    info_file = base + civitai.suffix + model.info_ext
                    model_info_file = base + civitai.suffix + '.main' + model.info_ext
                    md_info_file = base + civitai.suffix + '.md'
                    # check info file
                    if not os.path.isfile(info_file) or not os.path.isfile(model_info_file):
                        util.printD("Creating model info for: " + filename)
                        # get model's sha256
                        hash = util.gen_file_sha256(item)

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
                        
                        main_model_info = civitai.get_model_info_by_id(model_info['modelId'])
                        if main_model_info is None:
                            output = "Failed to get main_model_info"
                            util.printD(output)
                            return output+", check console log for detail"
                        
                        # write main model info to file
                        model.write_model_info(model_info_file, main_model_info)
                        
                        with open(md_info_file, 'w') as f:
                            if model_info['description']:
                                f.write(md(model_info['description']))
                            f.write('\n\n---\n\n')
                            if main_model_info['description']:
                                f.write(md(main_model_info['description']))

                    # set model_count
                    model_count = model_count+1

                    # check preview image
                    civitai.get_preview_image_by_model_path(item, max_size_preview, skip_nsfw_preview)
                    image_count = image_count+1


    # scan_log = "Done"

    output = f"Done. Scanned {model_count} models, checked {image_count} images"

    util.printD(output)

    return output



# Get model info by model type, name and url
# output is log info to display on markdown component
def get_model_info_by_input(model_type, model_name, model_url_or_id, max_size_preview, skip_nsfw_preview):
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



# check models' new version and output to UI as markdown doc
def check_models_new_version_to_md(model_types:list) -> str:
    new_versions = civitai.check_models_new_version_by_model_types(model_types, 1)

    count = 0
    output = ""
    if not new_versions:
        output = "No model has new version"
    else:
        output = "Found new version for following models:  <br>"
        for new_version in new_versions:
            count = count+1
            model_path, model_id, model_name, new_verion_id, new_version_name, description, download_url, img_url = new_version
            # in md, each part is something like this:
            # [model_name](model_url)
            # version description
            url = civitai.url_dict["modelPage"]+str(model_id)

            part = f'<b>Model: <a href="{url}" target="_blank">{model_name}</a></b> <br>'
            part = part + f"File: {model_path}  <br>"
            if download_url:
                part = part + f'New Version: <a href="{download_url}" target="_blank">{new_version_name}</a>'
            else:
                part = part + f"New Version: {new_version_name}"
            part = part + "  <br>"

            # description
            if description:
                part = part + description

            # preview image            
            if img_url:
                part = part + f"![]({img_url})  <br>"

            output = output + part

    util.printD(f"Done. Find {count} models have new version. Check UI for detail.")

    return output


