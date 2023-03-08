# -*- coding: UTF-8 -*-
# This extension can help you manage your models from civitai. It can download preview, add trigger words, open model page and use the prompt from preview image
# repo: https://github.com/butaixianran/



import modules.scripts as scripts
import gradio as gr
import os
import webbrowser
import requests
import random
import hashlib
import json
import shutil
import re
import modules
from modules import script_callbacks
from modules import shared
from scripts.lib import operator
from scripts.lib import setting


# load setting
setting.load()

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
    # with gr.Blocks(analytics_enabled=False) as civitai_helper:
    with gr.Blocks() as civitai_helper:

        # init
        low_memory_sha = setting.data["model"]["low_memory_sha"]
        max_size_preview = setting.data["model"]["max_size_preview"]
        skip_nsfw_preview = setting.data["model"]["skip_nsfw_preview"]
        open_url_with_js = setting.data["general"]["open_url_with_js"]
        check_model_version_at_startup = setting.data["general"]["check_model_version_at_startup"]


        # UI will have 3 tabs: 
        # Model Info: Scan model or force a model link to civitai model info by model id or url
        # Settging: Setting for general use, also can save setting for all tabs
        # Tool: handy functions, like making all model info readable.
        with gr.Tab("Model"):
            with gr.Row():
                low_memory_sha_ckb = gr.Checkbox(label="Memory Optimised SHA256", value=low_memory_sha, elem_id="ch_low_memory_sha_ckb")
                max_size_preview_ckb = gr.Checkbox(label="Download Max Size Preview", value=max_size_preview, elem_id="ch_max_size_preview_ckb")
                skip_nsfw_preview_ckb = gr.Checkbox(label="SKip NSFW Preview images", value=skip_nsfw_preview, elem_id="ch_skip_nsfw_preview_ckb")

            scan_model_btn = gr.Button(value="Scan model", elem_id="ch_scan_model_btn")

            gr.Markdown("Check console log window for detail, after clicking Scan button")


        # with gr.Tab("Settging"):

        # with gr.Tab("Tool"):

        # hidden component for js, not in any tab
        js_msg_txtbox = gr.Textbox(label="Request Msg From Js", visible=False, lines=1, value="", elem_id="ch_js_msg_txtbox")
        py_msg_txtbox = gr.Textbox(label="Response Msg From Python", visible=False, lines=1, value="", elem_id="ch_py_msg_txtbox")
        js_open_url_btn = gr.Button(value="Open Model Url", visible=False, elem_id="ch_js_open_url_btn")
        js_add_trigger_words_btn = gr.Button(value="Add Trigger Words", visible=False, elem_id="ch_js_add_trigger_words_btn")
        js_use_preview_prompt_btn = gr.Button(value="Use Prompt from Preview Image", visible=False, elem_id="ch_js_use_preview_prompt_btn")

        # ====events====
        scan_model_btn.click(operator.scan_model, inputs=[low_memory_sha_ckb, max_size_preview_ckb, skip_nsfw_preview_ckb])
        js_open_url_btn.click(operator.open_model_url, inputs=[js_msg_txtbox])
        js_add_trigger_words_btn.click(operator.add_trigger_words, inputs=[js_msg_txtbox], outputs=[txt2img_prompt, img2img_prompt])
        js_use_preview_prompt_btn.click(operator.use_preview_image_prompt, inputs=[js_msg_txtbox], outputs=[txt2img_prompt, txt2img_neg_prompt, img2img_prompt, img2img_neg_prompt])

    # the third parameter is the element id on html, with a "tab_" as prefix
    return (civitai_helper , "Civitai Helper", "civitai_helper"),

script_callbacks.on_ui_tabs(on_ui_tabs)


