# -*- coding: UTF-8 -*-
# handle msg between js and python side
import os
import json
import requests
import shutil
import webbrowser
from . import util
from . import model
from . import civitai
from . import msg



# scan model to generate SHA256, then use this SHA256 to get model info from civitai
def scan_model(low_memory_sha, max_size_preview, readable_model_info, skip_nsfw_preview):
    util.printD("Start scan_model")

    model_count = 0
    image_count = 0
    scan_log = ""
    for model_type, model_folder in model.folders.items():
        util.printD("Scanning path: " + model_folder)
        for root, dirs, files in os.walk(model_folder):
            for filename in files:
                # check ext
                item = os.path.join(root, filename)
                base, ext = os.path.splitext(item)
                if ext in model.exts:
                    # find a model
                    # set a Progress log
                    scan_log = "Scanned: " + str(model_count) + ", Scanning: "+ filename
                    # try to update to UI Here
                    # Is still trying to find a way

                    # get preview image
                    first_preview = base+".png"
                    sec_preview = base+".preview.png"
                    # get info file
                    info_file = base + civitai.suffix + model.info_ext
                    # check info file
                    if not os.path.isfile(info_file):
                        # get model's sha256
                        util.printD("Generate SHA256 for model: " + filename)
                        hash = util.gen_file_sha256(item, low_memory_sha)

                        if not hash:
                            util.printD("failed generate SHA256 for this file.")
                            return
                        
                        # use this sha256 to get model info from civitai
                        model_info = civitai.get_model_info_by_hash(hash)
                        if model_info is None:
                            util.printD("Fail to get model_info")
                            return
                        
                        # write model info to file
                        model.write_model_info(info_file, model_info)

                    # set model_count
                    model_count = model_count+1

                    # check preview image
                    if not os.path.isfile(sec_preview):
                        # need to download preview image
                        util.printD("Need preview image for this model")
                        # load model_info file
                        if os.path.isfile(info_file):
                            model_info = model.load_model_info(info_file)
                            if not model_info:
                                util.printD("Model Info is empty")
                                continue

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
                                                        img_url = civitai.get_full_size_image_url(img_url, img_dict["width"])

                                            util.download_file(img_url, sec_preview)
                                            image_count = image_count + 1
                                            # we only need 1 preview image
                                            break


    scan_log = "Done"

    util.printD("End scan_model")



# get civitai's model url and open it in browser
# parameter: model_type, search_term
def open_model_url(msg):
    util.printD("Start open_model_url")

    result = msg.parse_js_msg(msg)
    if not result:
        util.printD("Parsing js ms failed")
        return

    action, model_type, search_term, prompt, neg_prompt = result

    model_info = civitai.load_model_info_by_search_term(model_type, search_term)
    if not model_info:
        util.printD(f"Failed to get model info for {model_type} {search_term}")
        return

    if "modelId" not in model_info.keys():
        util.printD(f"Failed to get model id from info file for {model_type} {search_term}")
        return

    model_id = model_info["modelId"]
    if not model_id:
        util.printD(f"model id from info file of {model_type} {search_term} is None")
        return

    url = civitai.url_dict["modelPage"]+str(model_id)

    util.printD("Open Url: " + url)
    # open url
    webbrowser.open_new_tab(url)

    util.printD("End open_model_url")



# add trigger words to prompt
# parameter: model_type, search_term, prompt
# return: [new_prompt, new_prompt] - new prompt with trigger words, return twice for txt2img and img2img
def add_trigger_words(msg):
    util.printD("Start add_trigger_words")

    result = msg.parse_js_msg(msg)
    if not result:
        util.printD("Parsing js ms failed")
        return
    
    action, model_type, search_term, prompt, neg_prompt = result


    model_info = civitai.load_model_info_by_search_term(model_type, search_term)
    if not model_info:
        util.printD(f"Failed to get model info for {model_type} {search_term}")
        return [prompt, prompt]
    
    if "trainedWords" not in model_info.keys():
        util.printD(f"Failed to get trainedWords from info file for {model_type} {search_term}")
        return [prompt, prompt]
    
    trainedWords = model_info["trainedWords"]
    if not trainedWords:
        util.printD(f"No trainedWords from info file for {model_type} {search_term}")
        return [prompt, prompt]
    
    if len(trainedWords) == 0:
        util.printD(f"trainedWords from info file for {model_type} {search_term} is empty")
        return [prompt, prompt]
    
    # get ful trigger words
    trigger_words = ""
    for word in trainedWords:
        trigger_words = trigger_words + word + ", "

    new_prompt = prompt + " " + trigger_words
    util.printD("trigger_words: " + trigger_words)
    util.printD("prompt: " + prompt)
    util.printD("new_prompt: " + new_prompt)

    util.printD("End add_trigger_words")

    # add to prompt
    return [new_prompt, new_prompt]



# use preview image's prompt as prompt
# parameter: model_type, model_name, prompt, neg_prompt
# return: [new_prompt, new_neg_prompt, new_prompt, new_neg_prompt,] - return twice for txt2img and img2img
def use_preview_image_prompt(msg):
    util.printD("Start use_preview_image_prompt")

    result = msg.parse_js_msg(msg)
    if not result:
        util.printD("Parsing js ms failed")
        return
    
    action, model_type, search_term, prompt, neg_prompt = result


    model_info = civitai.load_model_info_by_search_term(model_type, search_term)
    if not model_info:
        util.printD(f"Failed to get model info for {model_type} {search_term}")
        return [prompt, neg_prompt, prompt, neg_prompt]
    
    if "images" not in model_info.keys():
        util.printD(f"Failed to get images from info file for {model_type} {search_term}")
        return [prompt, neg_prompt, prompt, neg_prompt]
    
    images = model_info["images"]
    if not images:
        util.printD(f"No images from info file for {model_type} {search_term}")
        return [prompt, neg_prompt, prompt, neg_prompt]
    
    if len(images) == 0:
        util.printD(f"images from info file for {model_type} {search_term} is empty")
        return [prompt, neg_prompt, prompt, neg_prompt]
    
    # get prompt from preview images' meta data
    preview_prompt = ""
    preview_neg_prompt = ""
    for img in images:
        if "meta" in img.keys():
            if img["meta"]:
                if "prompt" in img["meta"].keys():
                    if img["meta"]["prompt"]:
                        preview_prompt = img["meta"]["prompt"]
                
                if "negativePrompt" in img["meta"].keys():
                    if img["meta"]["negativePrompt"]:
                        preview_neg_prompt = img["meta"]["negativePrompt"]

                # we only need 1 prompt
                if preview_prompt:
                    break
            
    if not preview_prompt:
        util.printD(f"There is no prompt of {model_type} {search_term} in its preview image")
        return [prompt, neg_prompt, prompt, neg_prompt]
    
    util.printD("End use_preview_image_prompt")
    
    return [preview_prompt, preview_neg_prompt, preview_prompt, preview_neg_prompt]


