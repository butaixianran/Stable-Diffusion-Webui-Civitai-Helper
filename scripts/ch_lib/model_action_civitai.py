# -*- coding: UTF-8 -*-
# handle msg between js and python side
import os
import time
from . import util
from . import model
from . import civitai
from . import downloader


# scan model to generate SHA256, then use this SHA256 to get model info from civitai
# return output msg
def scan_model(scan_model_types, max_size_preview, skip_nsfw_preview):
    util.printD("Start scan_model")
    output = ""

    # check model types
    if not scan_model_types:
        output = "Model Types is None, can not scan."
        util.printD(output)
        return output
    
    model_types = []
    # check type if it is a string
    if type(scan_model_types) == str:
        model_types.append(scan_model_types)
    else:
        model_types = scan_model_types
    
    model_count = 0
    image_count = 0
    # scan_log = ""
    for model_type, model_folder in model.folders.items():
        if model_type not in model_types:
            continue

        util.printD("Scanning path: " + model_folder)
        for root, dirs, files in os.walk(model_folder, followlinks=True):
            for filename in files:
                # check ext
                item = os.path.join(root, filename)
                base, ext = os.path.splitext(item)
                if ext in model.exts:
                    # ignore vae file
                    if len(base) > 4:
                        if base[-4:] == model.vae_suffix:
                            # find .vae
                            util.printD("This is a vae file: " + filename)
                            continue

                    # find a model
                    # get info file
                    info_file = base + civitai.suffix + model.info_ext
                    # check info file
                    if not os.path.isfile(info_file):
                        util.printD("Creating model info for: " + filename)
                        # get model's sha256
                        hash = util.gen_file_sha256(item)

                        if not hash:
                            output = "failed generating SHA256 for model:" + filename
                            util.printD(output)
                            return output
                        
                        # use this sha256 to get model info from civitai
                        model_info = civitai.get_model_info_by_hash(hash)
                        # delay 1 second for ti
                        if model_type == "ti":
                            util.printD("Delay 1 second for TI")
                            time.sleep(1)

                        if model_info is None:
                            output = "Connect to Civitai API service failed. Wait a while and try again"
                            util.printD(output)
                            return output+", check console log for detail"

                        # write model info to file
                        model.write_model_info(info_file, model_info)

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
            # [version_name](download_url)
            # version description
            url = civitai.url_dict["modelPage"]+str(model_id)

            part = f'<div style="font-size:20px;margin:6px 0px;"><b>Model: <a href="{url}" target="_blank"><u>{model_name}</u></a></b></div>'
            part = part + f'<div style="font-size:16px">File: {model_path}</div>'
            if download_url:
                # replace "\" to "/" in model_path for windows
                model_path = model_path.replace('\\', '\\\\')
                part = part + f'<div style="font-size:16px;margin:6px 0px;">New Version: <u><a href="{download_url}" target="_blank" style="margin:0px 10px;">{new_version_name}</a></u>'
                # add js function to download new version into SD webui by python
                part = part + "    "
                # in embed HTML, onclick= will also follow a ", never a ', so have to write it as following
                part = part + f"<u><a href='#' style='margin:0px 10px;' onclick=\"ch_dl_model_new_version(event, '{model_path}', '{new_verion_id}', '{download_url}')\">[Download into SD]</a></u>"
                
            else:
                part = part + f'<div style="font-size:16px;margin:6px 0px;">New Version: {new_version_name}'
            part = part + '</div>'

            # description
            if description:
                part = part + '<blockquote style="font-size:16px;margin:6px 0px;">'+ description + '</blockquote><br>'

            # preview image            
            if img_url:
                part = part + f"<img src='{img_url}'><br>"
                

            output = output + part

    util.printD(f"Done. Find {count} models have new version. Check UI for detail.")

    return output


# get model info by url
def get_model_info_by_url(model_url_or_id:str) -> tuple:
    util.printD("Getting model info by: " + model_url_or_id)

    # parse model id
    model_id = civitai.get_model_id_from_url(model_url_or_id)
    if not model_id:
        util.printD("failed to parse model id from url or id")
        return    

    model_info = civitai.get_model_info_by_id(model_id)
    if model_info is None:
        util.printD("Connect to Civitai API service failed. Wait a while and try again")
        return
    
    if not model_info:
        util.printD("failed to get model info from url or id")
        return
    
    # parse model type, model name, subfolder, version from this model info
    # get model type
    if "type" not in model_info.keys():
        util.printD("model type is not in model_info")
        return
    
    civitai_model_type = model_info["type"]
    if civitai_model_type not in civitai.model_type_dict.keys():
        util.printD("This model type is not supported:"+civitai_model_type)
        return
    
    model_type = civitai.model_type_dict[civitai_model_type]

    # get model type
    if "name" not in model_info.keys():
        util.printD("model name is not in model_info")
        return

    model_name = model_info["name"]
    if not model_name:
        util.printD("model name is Empty")
        model_name = ""

    # get version list
    if "modelVersions" not in model_info.keys():
        util.printD("modelVersions is not in model_info")
        return
    
    modelVersions = model_info["modelVersions"]
    if not modelVersions:
        util.printD("modelVersions is Empty")
        return
    
    version_strs = []
    for version in modelVersions:
        # version name can not be used as id
        # version id is not readable
        # so , we use name_id as version string
        version_str = version["name"]+"_"+str(version["id"])
        version_strs.append(version_str)

    # get folder by model type
    folder = model.folders[model_type]
    # get subfolders
    subfolders = util.get_subfolders(folder)
    if not subfolders:
        subfolders = []

    # add default root folder
    subfolders.append("/")

    util.printD("Get following info for downloading:")
    util.printD(f"model_name:{model_name}")
    util.printD(f"model_type:{model_type}")
    util.printD(f"subfolders:{subfolders}")
    util.printD(f"version_strs:{version_strs}")

    return (model_info, model_name, model_type, subfolders, version_strs)

# get version info by version string
def get_ver_info_by_ver_str(version_str:str, model_info:dict) -> dict:
    if not version_str:
        util.printD("version_str is empty")
        return
    
    if not model_info:
        util.printD("model_info is None")
        return
    
    # get version list
    if "modelVersions" not in model_info.keys():
        util.printD("modelVersions is not in model_info")
        return

    modelVersions = model_info["modelVersions"]
    if not modelVersions:
        util.printD("modelVersions is Empty")
        return
    
    # find version by version_str
    version = None
    for ver in modelVersions:
        # version name can not be used as id
        # version id is not readable
        # so , we use name_id as version string
        ver_str = ver["name"]+"_"+str(ver["id"])
        if ver_str == version_str:
            # find version
            version = ver

    if not version:
        util.printD("can not find version by version string: " + version_str)
        return
    
    # get version id
    if "id" not in version.keys():
        util.printD("this version has no id")
        return
    
    return version


# get download url from model info by version string
# return - (version_id, download_url)
def get_id_and_dl_url_by_version_str(version_str:str, model_info:dict) -> tuple:
    if not version_str:
        util.printD("version_str is empty")
        return
    
    if not model_info:
        util.printD("model_info is None")
        return
    
    # get version list
    if "modelVersions" not in model_info.keys():
        util.printD("modelVersions is not in model_info")
        return

    modelVersions = model_info["modelVersions"]
    if not modelVersions:
        util.printD("modelVersions is Empty")
        return
    
    # find version by version_str
    version = None
    for ver in modelVersions:
        # version name can not be used as id
        # version id is not readable
        # so , we use name_id as version string
        ver_str = ver["name"]+"_"+str(ver["id"])
        if ver_str == version_str:
            # find version
            version = ver

    if not version:
        util.printD("can not find version by version string: " + version_str)
        return
    
    # get version id
    if "id" not in version.keys():
        util.printD("this version has no id")
        return
    
    version_id = version["id"]
    if not version_id:
        util.printD("version id is Empty")
        return

    # get download url
    if "downloadUrl" not in version.keys():
        util.printD("downloadUrl is not in this version")
        return
    
    downloadUrl = version["downloadUrl"]
    if not downloadUrl:
        util.printD("downloadUrl is Empty")
        return
    
    util.printD("Get Download Url: " + downloadUrl)
    
    return (version_id, downloadUrl)
    

# download model from civitai by input
# output to markdown log
def dl_model_by_input(model_info:dict, model_type:str, subfolder_str:str, version_str:str, max_size_preview:bool, skip_nsfw_preview:bool) -> str:

    output = ""

    if not model_info:
        output = "model_info is None"
        util.printD(output)
        return output
    
    if not model_type:
        output = "model_type is None"
        util.printD(output)
        return output
    
    if not subfolder_str:
        output = "subfolder string is None"
        util.printD(output)
        return output
    
    if not version_str:
        output = "version_str is None"
        util.printD(output)
        return output
    
    # get model root folder
    if model_type not in model.folders.keys():
        output = "Unknow model type: "+model_type
        util.printD(output)
        return output
    
    model_root_folder = model.folders[model_type]


    # get subfolder
    subfolder = ""
    if subfolder_str == "/" or subfolder_str == "\\":
        subfolder = ""
    elif subfolder_str[:1] == "/" or subfolder_str[:1] == "\\":
        subfolder = subfolder_str[1:]
    else:
        subfolder = subfolder_str

    # get model folder for downloading
    model_folder = os.path.join(model_root_folder, subfolder)
    if not os.path.isdir(model_folder):
        output = "Model folder is not a dir: "+ model_folder
        util.printD(output)
        return output
    
    # get version info
    ver_info = get_ver_info_by_ver_str(version_str, model_info)
    if not ver_info:
        output = "Fail to get version info, check console log for detail"
        util.printD(output)
        return output
    
    version_id = ver_info["id"]

    # get all download url from files info
    # some model versions have multiple files
    download_urls = []
    if "files" in ver_info.keys():
        for file_info in ver_info["files"]:
            if "downloadUrl" in file_info.keys():
                download_urls.append(file_info["downloadUrl"])

    if not len(download_urls):
        if "downloadUrl" in ver_info.keys():
            download_urls.append(ver_info["downloadUrl"])


    # check if this model is already existed
    r = civitai.search_local_model_info_by_version_id(model_folder, version_id)
    if r:
        output = "This model version is already existed"
        util.printD(output)
        return output
    
    # download
    filepath = ""
    for url in download_urls:
        model_filepath = downloader.dl(url, model_folder, None, None)
        if not model_filepath:
            output = "Downloading failed, check console log for detail"
            util.printD(output)
            return output
        
        if url == ver_info["downloadUrl"]:
            filepath = model_filepath

    if not filepath:
        filepath = model_filepath
    
    # get version info
    version_info = civitai.get_version_info_by_version_id(version_id)
    if not version_info:
        output = "Model downloaded, but failed to get version info, check console log for detail. Model saved to: " + filepath
        util.printD(output)
        return output

    # write version info to file
    base, ext = os.path.splitext(filepath)
    info_file = base + civitai.suffix + model.info_ext
    model.write_model_info(info_file, version_info)

    # then, get preview image
    civitai.get_preview_image_by_model_path(filepath, max_size_preview, skip_nsfw_preview)
    
    output = "Done. Model downloaded to: " + filepath
    util.printD(output)
    return output
