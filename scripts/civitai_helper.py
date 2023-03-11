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
from scripts.lib import model
from scripts.lib import js_action_civitai
from scripts.lib import model_action_civitai
from scripts.lib import setting
from scripts.lib import civitai
from scripts.lib import util


# init
model.get_custom_model_folder()
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

    # ====Event's function====
    def get_model_names_by_input(model_type, empty_info_only):
        names = civitai.get_model_names_by_input(model_type, empty_info_only)
        return model_name_drop.update(choices=names)



    # ====UI====
    # with gr.Blocks(analytics_enabled=False) as civitai_helper:
    with gr.Blocks(css="button {background-color: #228be6}") as civitai_helper:

        # init
        max_size_preview = setting.data["model"]["max_size_preview"]
        skip_nsfw_preview = setting.data["model"]["skip_nsfw_preview"]
        open_url_with_js = setting.data["general"]["open_url_with_js"]
        always_display = setting.data["general"]["always_display"]
        show_btn_on_thumb = setting.data["general"]["show_btn_on_thumb"]

        model_types = list(model.folders.keys())
        no_info_model_names = civitai.get_model_names_by_input("ckp", False)


        # with gr.Tab("Model"):
        with gr.Box():
            with gr.Column():
                gr.Markdown("### Scan Models for Civitai")
                with gr.Row():
                    max_size_preview_ckb = gr.Checkbox(label="Download Max Size Preview", value=max_size_preview, elem_id="ch_max_size_preview_ckb")
                    skip_nsfw_preview_ckb = gr.Checkbox(label="SKip NSFW Preview images", value=skip_nsfw_preview, elem_id="ch_skip_nsfw_preview_ckb")

                # with gr.Row():
                scan_model_civitai_btn = gr.Button(value="Scan", variant="primary", elem_id="ch_scan_model_civitai_btn")
                # with gr.Row():
                scan_model_log_md = gr.Markdown(value="Scanning takes time, just wait. Check console log for detail", elem_id="ch_scan_model_log_md")

        
        with gr.Box():
            with gr.Column():
                gr.Markdown("### Get Civitai Model Info by Model Page URL")
                with gr.Row():
                    model_type_drop = gr.Dropdown(choices=model_types, label="Model Type", value="ckp", multiselect=False)
                    empty_info_only_ckb = gr.Checkbox(label="Only Show Models have no Info file", value=False, elem_id="cn_empty_info_only_ckb")
                    model_name_drop = gr.Dropdown(choices=no_info_model_names, label="Model", value="ckp", multiselect=False)

                model_url_or_id = gr.Textbox(label="Civitai URL or Model ID", lines=1, value="")
                get_civitai_model_info_by_id_btn = gr.Button(value="Get Model Info from Civitai", variant="primary")
                get_model_by_id_log_md = gr.Markdown("")

        with gr.Box():
            with gr.Column():
                gr.Markdown("### Check models' new version")
                with gr.Row():
                    model_types_ckbg = gr.CheckboxGroup(choices=model_types, label="Model Types", value=["lora"])
                    check_models_new_version_btn = gr.Button(value="Check New Version from Civitai", variant="primary")

                check_models_new_version_log_md = gr.Markdown("It takes time, just wait. Check console log for detail")


        with gr.Box():
            with gr.Column():
                gr.Markdown("### Download Model")
                with gr.Row():
                    dl_model_type_drop = gr.Dropdown(choices=model_types, label="Model Type", value="ckp", multiselect=False)
                    dl_subfolder_drop = gr.Dropdown(choices=model_types, label="Sub-folder", value="", multiselect=False)

                dl_model_url_or_id = gr.Textbox(label="Civitai URL or Model ID", lines=1, value="")
                dl_civitai_model_by_id_btn = gr.Button(value="Download Model from Civitai", variant="primary")


        with gr.Box():
            with gr.Column():
                gr.Markdown("### Other Setting")
                with gr.Row():
                    open_url_with_js_ckb = gr.Checkbox(label="Open Url At Client Side", value=open_url_with_js, elem_id="ch_open_url_with_js_ckb")
                    always_display_ckb = gr.Checkbox(label="Always Display Buttons", value=always_display, elem_id="ch_always_display_ckb")
                    show_btn_on_thumb_ckb = gr.Checkbox(label="Show Button On Thumb Mode", value=show_btn_on_thumb, elem_id="ch_show_btn_on_thumb_ckb")

                save_setting_btn = gr.Button(value="Save Setting", elem_id="ch_save_setting_btn")
                general_log_md = gr.Markdown(value="", elem_id="ch_general_log_md")


        # ====Footer====
        gr.Markdown(f"<center>version:{util.version}</center>")

        # ====hidden component for js, not in any tab====
        js_msg_txtbox = gr.Textbox(label="Request Msg From Js", visible=False, lines=1, value="", elem_id="ch_js_msg_txtbox")
        py_msg_txtbox = gr.Textbox(label="Response Msg From Python", visible=False, lines=1, value="", elem_id="ch_py_msg_txtbox")
        js_open_url_btn = gr.Button(value="Open Model Url", visible=False, elem_id="ch_js_open_url_btn")
        js_add_trigger_words_btn = gr.Button(value="Add Trigger Words", visible=False, elem_id="ch_js_add_trigger_words_btn")
        js_use_preview_prompt_btn = gr.Button(value="Use Prompt from Preview Image", visible=False, elem_id="ch_js_use_preview_prompt_btn")

        # ====events====
        # Model
        scan_model_civitai_btn.click(model_action_civitai.scan_model, inputs=[max_size_preview_ckb, skip_nsfw_preview_ckb], outputs=scan_model_log_md)
        
        model_type_drop.change(get_model_names_by_input, inputs=[model_type_drop, empty_info_only_ckb], outputs=model_name_drop)
        empty_info_only_ckb.change(get_model_names_by_input, inputs=[model_type_drop, empty_info_only_ckb], outputs=model_name_drop)
        
        get_civitai_model_info_by_id_btn.click(model_action_civitai.get_model_info_by_input, inputs=[model_type_drop, model_name_drop, model_url_or_id, max_size_preview_ckb, skip_nsfw_preview_ckb], outputs=get_model_by_id_log_md)

        check_models_new_version_btn.click(model_action_civitai.check_models_new_version_to_md, inputs=model_types_ckbg, outputs=check_models_new_version_log_md)


        # General
        save_setting_btn.click(setting.save_from_input, inputs=[max_size_preview_ckb, skip_nsfw_preview_ckb, open_url_with_js_ckb, always_display_ckb, show_btn_on_thumb_ckb], outputs=general_log_md)

        # js action
        js_open_url_btn.click(js_action_civitai.open_model_url, inputs=[js_msg_txtbox, open_url_with_js_ckb], outputs=py_msg_txtbox)
        js_add_trigger_words_btn.click(js_action_civitai.add_trigger_words, inputs=[js_msg_txtbox], outputs=[txt2img_prompt, img2img_prompt])
        js_use_preview_prompt_btn.click(js_action_civitai.use_preview_image_prompt, inputs=[js_msg_txtbox], outputs=[txt2img_prompt, txt2img_neg_prompt, img2img_prompt, img2img_neg_prompt])

    # the third parameter is the element id on html, with a "tab_" as prefix
    return (civitai_helper , "Civitai Helper", "civitai_helper"),

script_callbacks.on_ui_tabs(on_ui_tabs)


