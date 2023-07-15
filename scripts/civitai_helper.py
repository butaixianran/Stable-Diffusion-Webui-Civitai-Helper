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
from scripts.ch_lib import model
from scripts.ch_lib import js_action_civitai
from scripts.ch_lib import model_action_civitai
from scripts.ch_lib import setting
from scripts.ch_lib import civitai
from scripts.ch_lib import util


# init

# root path
root_path = os.getcwd()

# extension path
extension_path = scripts.basedir()

model.get_custom_model_folder()
setting.load()

# set proxy
if setting.data["general"]["proxy"]:
    util.printD("Set Proxy: "+setting.data["general"]["proxy"])
    util.proxies = {
        "http": setting.data["general"]["proxy"],
        "https": setting.data["general"]["proxy"],
    }




def on_ui_tabs():
    # init
    # init_py_msg = {
    #     # relative extension path
    #     "extension_path": util.get_relative_path(extension_path, root_path),
    # }
    # init_py_msg_str = json.dumps(init_py_msg)


    # get prompt textarea
    # check modules/ui.py, search for txt2img_paste_fields
    # Negative prompt is the second element
    txt2img_prompt = modules.ui.txt2img_paste_fields[0][0]
    txt2img_neg_prompt = modules.ui.txt2img_paste_fields[1][0]
    img2img_prompt = modules.ui.img2img_paste_fields[0][0]
    img2img_neg_prompt = modules.ui.img2img_paste_fields[1][0]

    # ====Event's function====
    def get_model_names_by_input(model_type, empty_info_only):
        names = civitai.get_model_names_by_input(model_type, empty_info_only)
        return model_name_drop.update(choices=names)


    def get_model_info_by_url(url):
        r = model_action_civitai.get_model_info_by_url(url)

        model_info = {}
        model_name = ""
        model_type = ""
        subfolders = []
        version_strs = []
        if r:
            model_info, model_name, model_type, subfolders, version_strs = r

        return [model_info, model_name, model_type, dl_subfolder_drop.update(choices=subfolders), dl_version_drop.update(choices=version_strs)]

    # ====UI====
    with gr.Blocks(analytics_enabled=False) as civitai_helper:
    # with gr.Blocks(css=".block.padded {padding: 10px !important}") as civitai_helper:

        # init
        max_size_preview = setting.data["model"]["max_size_preview"]
        skip_nsfw_preview = setting.data["model"]["skip_nsfw_preview"]
        open_url_with_js = setting.data["general"]["open_url_with_js"]
        always_display = setting.data["general"]["always_display"]
        show_btn_on_thumb = setting.data["general"]["show_btn_on_thumb"]
        proxy = setting.data["general"]["proxy"]

        model_types = list(model.folders.keys())
        no_info_model_names = civitai.get_model_names_by_input("ckp", False)

        # session data
        dl_model_info = gr.State({})



        with gr.Box(elem_classes="ch_box"):
            with gr.Column():
                gr.Markdown("### Scan Models for Civitai")
                with gr.Row():
                    max_size_preview_ckb = gr.Checkbox(label="Download Max Size Preview", value=max_size_preview, elem_id="ch_max_size_preview_ckb")
                    skip_nsfw_preview_ckb = gr.Checkbox(label="Skip NSFW Preview Images", value=skip_nsfw_preview, elem_id="ch_skip_nsfw_preview_ckb")
                    scan_model_types_ckbg = gr.CheckboxGroup(choices=model_types, label="Model Types", value=model_types)

                # with gr.Row():
                scan_model_civitai_btn = gr.Button(value="Scan", variant="primary", elem_id="ch_scan_model_civitai_btn")
                # with gr.Row():
                scan_model_log_md = gr.Markdown(value="Scanning takes time, just wait. Check console log for detail", elem_id="ch_scan_model_log_md")

        
        with gr.Box(elem_classes="ch_box"):
            with gr.Column():
                gr.Markdown("### Get Model Info from Civitai by URL")
                gr.Markdown("Use this when scanning can not find a local model on civitai")
                with gr.Row():
                    model_type_drop = gr.Dropdown(choices=model_types, label="Model Type", value="ckp", multiselect=False)
                    empty_info_only_ckb = gr.Checkbox(label="Only Show Models have no Info", value=False, elem_id="ch_empty_info_only_ckb", elem_classes="ch_vpadding")
                    model_name_drop = gr.Dropdown(choices=no_info_model_names, label="Model", value="ckp", multiselect=False)

                model_url_or_id_txtbox = gr.Textbox(label="Civitai URL", lines=1, value="")
                get_civitai_model_info_by_id_btn = gr.Button(value="Get Model Info from Civitai", variant="primary")
                get_model_by_id_log_md = gr.Markdown("")

        with gr.Box(elem_classes="ch_box"):
            with gr.Column():
                gr.Markdown("### Download Model")
                with gr.Row():
                    dl_model_url_or_id_txtbox = gr.Textbox(label="Civitai URL", lines=1, value="")
                    dl_model_info_btn = gr.Button(value="1. Get Model Info by Civitai Url", variant="primary")

                gr.Markdown(value="2. Pick Subfolder and Model Version")
                with gr.Row():
                    dl_model_name_txtbox = gr.Textbox(label="Model Name", interactive=False, lines=1, value="")
                    dl_model_type_txtbox = gr.Textbox(label="Model Type", interactive=False, lines=1, value="")
                    dl_subfolder_drop = gr.Dropdown(choices=[], label="Sub-folder", value="", interactive=True, multiselect=False)
                    dl_version_drop = gr.Dropdown(choices=[], label="Model Version", value="", interactive=True, multiselect=False)
                    dl_all_ckb = gr.Checkbox(label="Download All files", value=False, elem_id="ch_dl_all_ckb", elem_classes="ch_vpadding")
                
                dl_civitai_model_by_id_btn = gr.Button(value="3. Download Model", variant="primary")
                dl_log_md = gr.Markdown(value="Check Console log for Downloading Status")

        with gr.Box(elem_classes="ch_box"):
            with gr.Column():
                gr.Markdown("### Check models' new version")
                with gr.Row():
                    model_types_ckbg = gr.CheckboxGroup(choices=model_types, label="Model Types", value=["ti", "hyper", "ckp", "lora", "lycoris"])
                    check_models_new_version_btn = gr.Button(value="Check New Version from Civitai", variant="primary")

                check_models_new_version_log_md = gr.HTML("It takes time, just wait. Check console log for detail")

        with gr.Box(elem_classes="ch_box"):
            with gr.Column():
                gr.Markdown("### Other Setting")
                with gr.Row():
                    open_url_with_js_ckb = gr.Checkbox(label="Open Url At Client Side", value=open_url_with_js, elem_id="ch_open_url_with_js_ckb")
                    always_display_ckb = gr.Checkbox(label="Always Display Buttons", value=always_display, elem_id="ch_always_display_ckb")
                    show_btn_on_thumb_ckb = gr.Checkbox(label="Show Button On Thumb Mode", value=show_btn_on_thumb, elem_id="ch_show_btn_on_thumb_ckb")

                proxy_txtbox = gr.Textbox(label="Proxy", interactive=True, lines=1, value=proxy, info="format: http://127.0.0.1:port")

                save_setting_btn = gr.Button(value="Save Setting")
                general_log_md = gr.Markdown(value="")


        # ====Footer====
        gr.Markdown(f"<center>version:{util.version}</center>")

        # ====hidden component for js, not in any tab====
        js_msg_txtbox = gr.Textbox(label="Request Msg From Js", visible=False, lines=1, value="", elem_id="ch_js_msg_txtbox")
        py_msg_txtbox = gr.Textbox(label="Response Msg From Python", visible=False, lines=1, value="", elem_id="ch_py_msg_txtbox")

        js_open_url_btn = gr.Button(value="Open Model Url", visible=False, elem_id="ch_js_open_url_btn")
        js_add_trigger_words_btn = gr.Button(value="Add Trigger Words", visible=False, elem_id="ch_js_add_trigger_words_btn")
        js_use_preview_prompt_btn = gr.Button(value="Use Prompt from Preview Image", visible=False, elem_id="ch_js_use_preview_prompt_btn")
        js_dl_model_new_version_btn = gr.Button(value="Download Model's new version", visible=False, elem_id="ch_js_dl_model_new_version_btn")

        # ====events====
        # Scan Models for Civitai
        scan_model_civitai_btn.click(model_action_civitai.scan_model, inputs=[scan_model_types_ckbg, max_size_preview_ckb, skip_nsfw_preview_ckb], outputs=scan_model_log_md)

        # Get Civitai Model Info by Model Page URL
        model_type_drop.change(get_model_names_by_input, inputs=[model_type_drop, empty_info_only_ckb], outputs=model_name_drop)
        empty_info_only_ckb.change(get_model_names_by_input, inputs=[model_type_drop, empty_info_only_ckb], outputs=model_name_drop)

        get_civitai_model_info_by_id_btn.click(model_action_civitai.get_model_info_by_input, inputs=[model_type_drop, model_name_drop, model_url_or_id_txtbox, max_size_preview_ckb, skip_nsfw_preview_ckb], outputs=get_model_by_id_log_md)

        # Download Model
        dl_model_info_btn.click(get_model_info_by_url, inputs=dl_model_url_or_id_txtbox, outputs=[dl_model_info, dl_model_name_txtbox, dl_model_type_txtbox, dl_subfolder_drop, dl_version_drop])
        dl_civitai_model_by_id_btn.click(model_action_civitai.dl_model_by_input, inputs=[dl_model_info, dl_model_type_txtbox, dl_subfolder_drop, dl_version_drop, dl_all_ckb, max_size_preview_ckb, skip_nsfw_preview_ckb], outputs=dl_log_md)

        # Check models' new version
        check_models_new_version_btn.click(model_action_civitai.check_models_new_version_to_md, inputs=model_types_ckbg, outputs=check_models_new_version_log_md)

        # Other Setting
        save_setting_btn.click(setting.save_from_input, inputs=[max_size_preview_ckb, skip_nsfw_preview_ckb, open_url_with_js_ckb, always_display_ckb, show_btn_on_thumb_ckb, proxy_txtbox], outputs=general_log_md)

        # js action
        js_open_url_btn.click(js_action_civitai.open_model_url, inputs=[js_msg_txtbox, open_url_with_js_ckb], outputs=py_msg_txtbox)
        js_add_trigger_words_btn.click(js_action_civitai.add_trigger_words, inputs=[js_msg_txtbox], outputs=[txt2img_prompt, img2img_prompt])
        js_use_preview_prompt_btn.click(js_action_civitai.use_preview_image_prompt, inputs=[js_msg_txtbox], outputs=[txt2img_prompt, txt2img_neg_prompt, img2img_prompt, img2img_neg_prompt])
        js_dl_model_new_version_btn.click(js_action_civitai.dl_model_new_version, inputs=[js_msg_txtbox, max_size_preview_ckb, skip_nsfw_preview_ckb], outputs=dl_log_md)

    # the third parameter is the element id on html, with a "tab_" as prefix
    return (civitai_helper , "Civitai Helper", "civitai_helper"),

script_callbacks.on_ui_tabs(on_ui_tabs)



