# -*- coding: UTF-8 -*-
# This extension can help you manage your models from civitai. It can download preview, add trigger words, open model page and use the prompt from preview image
# repo: https://github.com/butaixianran/

import hashlib
import json
import os
import shutil
import webbrowser

import gradio as gr
import requests

import modules
from modules import script_callbacks
from modules import shared

# from modules import images
# from modules.processing import process_images, Processed
# from modules.processing import Processed
# from modules.shared import opts, cmd_opts, state

# print for debugging
def printD(msg):
    print(f"Civitai Helper: {msg}")


printD("Current Model folder:")
if shared.cmd_opts.embeddings_dir:
    printD("ti: " + shared.cmd_opts.embeddings_dir)
else:
    printD("shared.cmd_opts.embeddings_dir is None")

if shared.cmd_opts.hypernetwork_dir:
    printD("hypernetwork_dir: " + shared.cmd_opts.hypernetwork_dir)
else:
    printD("shared.cmd_opts.embeddings_dir is None")


if shared.cmd_opts.ckpt_dir:
    printD("ckpt_dir: " + shared.cmd_opts.ckpt_dir)
else:
    printD("shared.cmd_opts.ckpt_dir is None")


if shared.cmd_opts.lora_dir:
    printD("lora_dir: " + shared.cmd_opts.lora_dir)
else:
    printD("shared.cmd_opts.lora_dir is None")


# init
model_folders = {
    "ti": shared.cmd_opts.embeddings_dir or "embeddings",
    "hyper": shared.cmd_opts.hypernetwork_dir or os.path.join("models", "hypernetworks"),
    "ckp": shared.cmd_opts.ckpt_dir or os.path.join("models", "Stable-diffusion"),
    "lora": shared.cmd_opts.lora_dir or os.path.join("models", "Lora"),
}

model_exts = (".bin", ".pt", ".safetensors", ".ckpt")
model_info_exts = ".info"
civitai_info_suffix = ".civitai"
civitai_hash_api_url = "https://civitai.com/api/v1/model-versions/by-hash/"

# js action list
js_actions = ("open_url", "add_trigger_words", "use_preview_prompt")

root_path = os.getcwd()


def gen_file_sha256(filename):
    ''' calculate file sha256 '''
    hash_value = ""
    with open(filename, "rb") as f:
        sha256obj = hashlib.sha256()
        sha256obj.update(f.read())
        hash_value = sha256obj.hexdigest()

    printD("sha256: " + hash_value)
    return hash_value

def gen_file_sha256_low_memory(filename):
    printD("Using Memory Optimised SHA256")
    hash_sha256 = hashlib.sha256()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)

    hash_value =  hash_sha256.hexdigest()
    printD("sha256: " + hash_value)
    return hash_value

# scan model to generate SHA256, then use this SHA256 to get model info from civitai
def scan_model(skip_nsfw_preview, low_memory_sha):
    printD("Start scan_model")

    for model_type, model_folder in model_folders.items():
        folder_path = os.path.join(root_path, model_folder)
        printD("Scanning path: " + folder_path)
        for root, dirs, files in os.walk(folder_path):
            for filename in files:
                # check ext
                item = os.path.join(root, filename)
                base, ext = os.path.splitext(item)
                if ext in model_exts:
                    # find a model
                    # get preview image
                    sec_preview = base+".preview.png"
                    # get info file
                    info_file = base + civitai_info_suffix + model_info_exts
                    # check info file
                    if not os.path.isfile(info_file):
                        # get model's sha256
                        printD("Generate SHA256 for model: " + filename)
                        hash = ""
                        if low_memory_sha:
                            hash = gen_file_sha256_low_memory(item)
                        else:
                            hash = gen_file_sha256(item)

                        if not hash:
                            printD("failed generate SHA256 for this file.")
                            return
                        
                        # use this sha256 to get model info from civitai
                        printD("Request model info from civitai")
                        r = requests.get(civitai_hash_api_url+hash)
                        if not r.ok:
                            if r.status_code == 404:
                                # this is not a civitai model
                                printD("Civitai does not have this model")
                                printD("Write empty model info file")
                                with open(info_file, 'w') as f:
                                    f.write(json.dumps({}))
                                # go to next file
                                continue
                            else:
                                printD("Get errorcode: " + str(r.status_code))
                                printD(r.text)
                                return

                        # try to get content
                        content = None
                        try:
                            content = r.json()
                        except Exception as e:
                            printD("Parse response json failed")
                            printD(str(e))
                            printD("response:")
                            printD(r.text)
                            return
                        
                        if not content:
                            printD("error, content from civitai is None")
                            return
                        
                        # write model info to file
                        printD("Write model info to file: " + info_file)
                        with open(info_file, 'w') as f:
                            data = json.dumps(content)
                            f.write(data)

                        # check preview image
                        if not os.path.isfile(sec_preview):
                            # need to download preview image
                            printD("Need preview image for this model")
                            if content["images"]:
                                for img_dict in content["images"]:
                                    if "nsfw" in img_dict.keys():
                                        if img_dict["nsfw"]:
                                            printD("This image is NSFW")
                                            if skip_nsfw_preview:
                                                printD("Skip NSFW image")
                                                continue
                                    
                                    if "url" in img_dict.keys():
                                        printD("Sending request for image: " + img_dict["url"])
                                        # get image
                                        img_r = requests.get(img_dict["url"], stream=True)
                                        if not img_r.ok:
                                            printD("Get errorcode: " + str(r.status_code))
                                            printD(r.text)
                                            return
                                        
                                        # write to file
                                        with open(sec_preview, 'wb') as f:
                                            img_r.raw.decode_content = True
                                            shutil.copyfileobj(img_r.raw, f)

                                        printD("Created Preview image: " + sec_preview)

                                        # we only need 1 preview image
                                        break

                # for testing, we only check 1 model for each type
                # break

    printD("End scan_model")



# handle request from javascript
# parameter: msg - msg from js
# return: (action, model_type, search_term, prompt, neg_prompt)
def parse_js_msg(msg):
    printD("Start parse js msg")
    msg_dict = json.loads(msg)

    if "action" not in msg_dict.keys():
        printD("Can not find action from js request")
        return
    
    if "model_type" not in msg_dict.keys():
        printD("Can not find model type from js request")
        return
    
    if "search_term" not in msg_dict.keys():
        printD("Can not find search_term from js request")
        return
    
    if "prompt" not in msg_dict.keys():
        printD("Can not find prompt from js request")
        return
    
    if "neg_prompt" not in msg_dict.keys():
        printD("Can not find neg_prompt from js request")
        return
    
    action = msg_dict["action"]
    model_type = msg_dict["model_type"]
    search_term = msg_dict["search_term"]
    prompt = msg_dict["prompt"]
    neg_prompt = msg_dict["neg_prompt"]

    if not action:
        printD("Action from js request is None")
        return

    if not model_type:
        printD("model_type from js request is None")
        return
    
    if not search_term:
        printD("search_term from js request is None")
        return
    

    if action not in js_actions:
        printD("Unknown action: " + action)
        return

    if model_type not in model_folders.keys():
        printD("Unknown model_type: " + model_type)
        return
    
    printD("End parse js msg")

    return (action, model_type, search_term, prompt, neg_prompt)


# get model info file's content by model type and model name
# parameter: model_type, search_term
# return: model_info_dict
def get_model_info(model_type, search_term):
    if model_type not in model_folders.keys():
        printD("unknown model type: " + model_type)
        return None
    
    # search_term = subfolderpath + model name + ext. And it always start with a / even there is no sub folder
    base, ext = os.path.splitext(search_term)
    model_info_base = base
    if base[:1] == "/":
        model_info_base = base[1:]


    model_folder = model_folders[model_type]
    model_info_filename = model_info_base + civitai_info_suffix + model_info_exts
    model_info_filepath = os.path.join(root_path, model_folder, model_info_filename)

    if not os.path.isfile(model_info_filepath):
        printD("Can not find model info file: " + model_info_filepath)
        return None
    
    model_info = None
    with open(model_info_filepath, 'r') as f:
        try:
            model_info = json.load(f)
        except Exception as e:
            printD("Selected file is not json: " + model_info_filepath)
            printD(e)
            return None
        
    return model_info


# get civitai's model url and open it in browser
# parameter: model_type, search_term
def open_model_url(msg):
    printD("Start open_model_url")

    result = parse_js_msg(msg)
    if not result:
        printD("Parsing js ms failed")
        return

    action, model_type, search_term, prompt, neg_prompt = result

    model_info = get_model_info(model_type, search_term)
    if not model_info:
        printD(f"Failed to get model info for {model_type} {search_term}")
        return

    if "modelId" not in model_info.keys():
        printD(f"Failed to get model id from info file for {model_type} {search_term}")
        return

    model_id = model_info["modelId"]
    if not model_id:
        printD(f"model id from info file of {model_type} {search_term} is None")
        return

    url = "https://civitai.com/models/"+str(model_id)

    printD("Open Url: " + url)
    # open url
    webbrowser.open_new_tab(url)

    printD("End open_model_url")


# add trigger words to prompt
# parameter: model_type, search_term, prompt
# return: [new_prompt, new_prompt] - new prompt with trigger words, return twice for txt2img and img2img
def add_trigger_words(msg):
    printD("Start add_trigger_words")

    result = parse_js_msg(msg)
    if not result:
        printD("Parsing js ms failed")
        return
    
    action, model_type, search_term, prompt, neg_prompt = result


    model_info = get_model_info(model_type, search_term)
    if not model_info:
        printD(f"Failed to get model info for {model_type} {search_term}")
        return [prompt, prompt]
    
    if "trainedWords" not in model_info.keys():
        printD(f"Failed to get trainedWords from info file for {model_type} {search_term}")
        return [prompt, prompt]
    
    trainedWords = model_info["trainedWords"]
    if not trainedWords:
        printD(f"No trainedWords from info file for {model_type} {search_term}")
        return [prompt, prompt]
    
    if len(trainedWords) == 0:
        printD(f"trainedWords from info file for {model_type} {search_term} is empty")
        return [prompt, prompt]
    
    # get ful trigger words
    trigger_words = ""
    for word in trainedWords:
        trigger_words = trigger_words + word + ", "

    new_prompt = prompt + " " + trigger_words
    printD("trigger_words: " + trigger_words)
    printD("prompt: " + prompt)
    printD("new_prompt: " + new_prompt)

    printD("End add_trigger_words")

    # add to prompt
    return [new_prompt, new_prompt]



# use preview image's prompt as prompt
# parameter: model_type, model_name, prompt, neg_prompt
# return: [new_prompt, new_neg_prompt, new_prompt, new_neg_prompt,] - return twice for txt2img and img2img
def use_preview_image_prompt(msg):
    printD("Start use_preview_image_prompt")

    result = parse_js_msg(msg)
    if not result:
        printD("Parsing js ms failed")
        return
    
    action, model_type, search_term, prompt, neg_prompt = result


    model_info = get_model_info(model_type, search_term)
    if not model_info:
        printD(f"Failed to get model info for {model_type} {search_term}")
        return [prompt, neg_prompt, prompt, neg_prompt]
    
    if "images" not in model_info.keys():
        printD(f"Failed to get images from info file for {model_type} {search_term}")
        return [prompt, neg_prompt, prompt, neg_prompt]
    
    images = model_info["images"]
    if not images:
        printD(f"No images from info file for {model_type} {search_term}")
        return [prompt, neg_prompt, prompt, neg_prompt]
    
    if len(images) == 0:
        printD(f"images from info file for {model_type} {search_term} is empty")
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
        printD(f"There is no prompt of {model_type} {search_term} in its preview image")
        return [prompt, neg_prompt, prompt, neg_prompt]
    
    printD("End use_preview_image_prompt")
    
    return [preview_prompt, preview_neg_prompt, preview_prompt, preview_neg_prompt]




def on_ui_tabs():
    # init

    # get prompt textarea
    # UI structure
    # check modules/ui.py, search for txt2img_paste_fields
    # Negative prompt is the second element
    txt2img_prompt = modules.ui.txt2img_paste_fields[0][0]
    txt2img_neg_prompt = modules.ui.txt2img_paste_fields[1][0]
    img2img_prompt = modules.ui.img2img_paste_fields[0][0]
    img2img_neg_prompt = modules.ui.img2img_paste_fields[1][0]

    # ====UI====
    with gr.Blocks(analytics_enabled=False) as civitai_helper:
        # info        
        with gr.Row():
            skip_nsfw_preview_ckb = gr.Checkbox(label="SKip NSFW Preview images", value=False, elem_id="ch_skip_nsfw_preview_ckb")
            low_memory_sha_ckb = gr.Checkbox(label="Memory Optimised SHA256", value=False, elem_id="ch_low_memory_sha_ckb")

        scan_model_btn = gr.Button(value="Scan model", elem_id="ch_scan_model_btn")

        gr.Markdown("Check console log window for detail, after clicking Scan button")

        # hidden component for js
        js_msg_txtbox = gr.Textbox(label="Request Msg From Js", visible=False, lines=1, value="", elem_id="ch_js_msg_txtbox")
        js_open_url_btn = gr.Button(value="Open Model Url", visible=False, elem_id="ch_js_open_url_btn")
        js_add_trigger_words_btn = gr.Button(value="Add Trigger Words", visible=False, elem_id="ch_js_add_trigger_words_btn")
        js_use_preview_prompt_btn = gr.Button(value="Use Prompt from Preview Image", visible=False, elem_id="ch_js_use_preview_prompt_btn")

        # ====events====
        scan_model_btn.click(scan_model, inputs=[skip_nsfw_preview_ckb, low_memory_sha_ckb])
        js_open_url_btn.click(open_model_url, inputs=[js_msg_txtbox])
        js_add_trigger_words_btn.click(add_trigger_words, inputs=[js_msg_txtbox], outputs=[txt2img_prompt, img2img_prompt])
        js_use_preview_prompt_btn.click(use_preview_image_prompt, inputs=[js_msg_txtbox], outputs=[txt2img_prompt, txt2img_neg_prompt, img2img_prompt, img2img_neg_prompt])

    # the third parameter is the element id on html, with a "tab_" as prefix
    return (civitai_helper , "Civitai Helper", "civitai_helper"),

script_callbacks.on_ui_tabs(on_ui_tabs)
