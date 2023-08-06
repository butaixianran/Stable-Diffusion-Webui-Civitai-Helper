"use strict";


function ch_convert_file_path_to_url(path){
    let prefix = "file=";
    let path_to_url = path.replaceAll('\\', '/');
    return prefix+path_to_url;
}

function ch_img_node_str(path){
    return `<img src='${ch_convert_file_path_to_url(path)}' style="width:24px"/>`;
}


function ch_gradio_version(){
    let foot = gradioApp().getElementById("footer");
    if (!foot){return null;}

    let versions = foot.querySelector(".versions");
    if (!versions){return null;}

    if (versions.textContent.indexOf("gradio: 3.16.2")>0) {
        return "3.16.2";
    } else {
        return "3.23.0";
    }

}


// send msg to python side by filling a hidden text box
// then will click a button to trigger an action
// msg is an object, not a string, will be stringify in this function
function send_ch_py_msg(msg){
    console.log("run send_ch_py_msg");
    let js_msg_txtbox = gradioApp().querySelector("#ch_js_msg_txtbox textarea");
    if (js_msg_txtbox && msg) {
        // fill to msg box
        js_msg_txtbox.value = JSON.stringify(msg);
        js_msg_txtbox.dispatchEvent(new Event("input"));
    }

}

// get msg from python side from a hidden textbox
// normally this is an old msg, need to wait for a new msg
function get_ch_py_msg(){
    console.log("run get_ch_py_msg");
    const py_msg_txtbox = gradioApp().querySelector("#ch_py_msg_txtbox textarea");
    if (py_msg_txtbox && py_msg_txtbox.value) {
        console.log("find py_msg_txtbox");
        console.log("py_msg_txtbox value: ");
        console.log(py_msg_txtbox.value);
        return py_msg_txtbox.value;
    } else {
        return "";
    }
}


// get msg from python side from a hidden textbox
// it will try once in every sencond, until it reach the max try times
const get_new_ch_py_msg = (max_count=3) => new Promise((resolve, reject) => {
    console.log("run get_new_ch_py_msg");

    let count = 0;
    let new_msg = "";
    let find_msg = false;
    const interval = setInterval(() => {
        const py_msg_txtbox = gradioApp().querySelector("#ch_py_msg_txtbox textarea");
        count++;

        if (py_msg_txtbox && py_msg_txtbox.value) {
            console.log("find py_msg_txtbox");
            console.log("py_msg_txtbox value: ");
            console.log(py_msg_txtbox.value);

            new_msg = py_msg_txtbox.value;
            if (new_msg != "") {
                find_msg = true;
            }
        }

        if (find_msg) {
            //clear msg in both sides
            py_msg_txtbox.value = "";
            py_msg_txtbox.dispatchEvent(new Event("input"));

            resolve(new_msg);
            clearInterval(interval);
        } else if (count > max_count) {
            //clear msg in both sides
            py_msg_txtbox.value = "";
            py_msg_txtbox.dispatchEvent(new Event("input"));

            reject('');
            clearInterval(interval);
        }

    }, 1000);
});


function getActiveTabType() {
    const currentTab = get_uiCurrentTabContent();
    switch (currentTab.id) {
        case "tab_txt2img":
            return "txt2img";
        case "tab_img2img":
            return "img2img";
    }
    return null;
}



function getActivePrompt() {
    const currentTab = get_uiCurrentTabContent();
    switch (currentTab.id) {
        case "tab_txt2img":
            return currentTab.querySelector("#txt2img_prompt textarea");
        case "tab_img2img":
            return currentTab.querySelector("#img2img_prompt textarea");
    }
    return null;
}

function getActiveNegativePrompt() {
    const currentTab = get_uiCurrentTabContent();
    switch (currentTab.id) {
        case "tab_txt2img":
            return currentTab.querySelector("#txt2img_neg_prompt textarea");
        case "tab_img2img":
            return currentTab.querySelector("#img2img_neg_prompt textarea");
    }
    return null;
}


//button's click function
async function open_model_url(event, model_type, search_term){
    console.log("start open_model_url");

    //get hidden components of extension
    let js_open_url_btn = gradioApp().getElementById("ch_js_open_url_btn");
    if (!js_open_url_btn) {
        return;
    }


    //msg to python side
    let msg = {
        "action": "",
        "model_type": "",
        "search_term": "",
        "prompt": "",
        "neg_prompt": "",
    };


    msg["action"] = "open_url";
    msg["model_type"] = model_type;
    msg["search_term"] = search_term;
    msg["prompt"] = "";
    msg["neg_prompt"] = "";

    // fill to msg box
    send_ch_py_msg(msg);

    //click hidden button
    js_open_url_btn.click();

    // stop parent event
    event.stopPropagation();
    event.preventDefault();

    //check response msg from python
    let new_py_msg = await get_new_ch_py_msg();
    console.log("new_py_msg:");
    console.log(new_py_msg);

    //check msg
    if (new_py_msg) {
        let py_msg_json = JSON.parse(new_py_msg);
        //check for url
        if (py_msg_json && py_msg_json.content) {
            if (py_msg_json.content.url) {
                window.open(py_msg_json.content.url, "_blank");
            }

        }


    }


    console.log("end open_model_url");


}

function add_trigger_words(event, model_type, search_term){
    console.log("start add_trigger_words");

    //get hidden components of extension
    let js_add_trigger_words_btn = gradioApp().getElementById("ch_js_add_trigger_words_btn");
    if (!js_add_trigger_words_btn) {
        return;
    }


    //msg to python side
    let msg = {
        "action": "",
        "model_type": "",
        "search_term": "",
        "prompt": "",
        "neg_prompt": "",
    };

    msg["action"] = "add_trigger_words";
    msg["model_type"] = model_type;
    msg["search_term"] = search_term;
    msg["neg_prompt"] = "";

    // get active prompt
    let act_prompt = getActivePrompt();
    msg["prompt"] = act_prompt.value;

    // fill to msg box
    send_ch_py_msg(msg);

    //click hidden button
    js_add_trigger_words_btn.click();

    console.log("end add_trigger_words");

    event.stopPropagation();
    event.preventDefault();


}

function use_preview_prompt(event, model_type, search_term){
    console.log("start use_preview_prompt");

    //get hidden components of extension
    let js_use_preview_prompt_btn = gradioApp().getElementById("ch_js_use_preview_prompt_btn");
    if (!js_use_preview_prompt_btn) {
        return;
    }

    //msg to python side
    let msg = {
        "action": "",
        "model_type": "",
        "search_term": "",
        "prompt": "",
        "neg_prompt": "",
    };

    msg["action"] = "use_preview_prompt";
    msg["model_type"] = model_type;
    msg["search_term"] = search_term;

    // get active prompt
    let act_prompt = getActivePrompt();
    msg["prompt"] = act_prompt.value;

    // get active neg prompt
    let neg_prompt = getActiveNegativePrompt();
    msg["neg_prompt"] = neg_prompt.value;

    // fill to msg box
    send_ch_py_msg(msg);

    //click hidden button
    js_use_preview_prompt_btn.click();

    console.log("end use_preview_prompt");

    event.stopPropagation();
    event.preventDefault();

}



// download model's new version into SD at python side
function ch_dl_model_new_version(event, model_path, version_id, download_url){
    console.log("start ch_dl_model_new_version");

    // must confirm before downloading
    let dl_confirm = "\nConfirm to download.\n\nCheck Download Model Section's log and console log for detail.";
    if (!confirm(dl_confirm)) {
        return;
    }

    //get hidden components of extension
    let js_dl_model_new_version_btn = gradioApp().getElementById("ch_js_dl_model_new_version_btn");
    if (!js_dl_model_new_version_btn) {
        return;
    }

    //msg to python side
    let msg = {
        "action": "",
        "model_path": "",
        "version_id": "",
        "download_url": "",
    };

    msg["action"] = "dl_model_new_version";
    msg["model_path"] = model_path;
    msg["version_id"] = version_id;
    msg["download_url"] = download_url;

    // fill to msg box
    send_ch_py_msg(msg);

    //click hidden button
    js_dl_model_new_version_btn.click();

    console.log("end dl_model_new_version");

    event.stopPropagation();
    event.preventDefault();


}

function waitForEditor(page, type, name) {
    let id = page + '_' + type + '_edit_user_metadata';

    return new Promise(resolve => {
        let name_field;
        let editor = document.getElementById(id);

        let popup = document.querySelector(".global-popup");
        if (popup != null) {
            // hide the editor window so it doesn't get in the user's
            // way while we wait for the replace preview functionality
            // to become available.
            popup.style.display = "none";
        }

        // not only do we need to wait for the editor,
        // but also for it to populate with the model metadata.
        if (editor != null) {
            name_field = editor.querySelector('.extra-network-name');
            if (name_field.textContent.trim() == name) {
                return resolve(editor);
            }
        }

        const observer = new MutationObserver(() => {
            let editor = document.getElementById(id);
            let name_field;
            if (editor != null) {
                name_field = editor.querySelector('.extra-network-name');
                if (name_field.textContent.trim() == name) {
                    resolve(editor);
                    observer.disconnect();
                }
            }
        });

        observer.observe(document.body, {
            subtree: true,
            childList: true,
        });
    });
}

onUiLoaded(() => {

    //get gradio version
    let gradio_ver = ch_gradio_version();
    console.log("gradio_ver:" + gradio_ver);

    // get all extra network tabs
    let tab_prefix_list = ["txt2img", "img2img"];
    let model_type_list = ["textual_inversion", "hypernetworks", "checkpoints", "lora", "lycoris"];
    let cardid_suffix = "cards";

    //get init py msg
    // let init_py_msg_str = get_ch_py_msg();
    // let extension_path = "";
    // if (!init_py_msg_str) {
    //     console.log("Can not get init_py_msg");
    // } else {
    //     init_py_msg = JSON.parse(init_py_msg_str);
    //     if (init_py_msg) {
    //         extension_path = init_py_msg.extension_path;
    //         console.log("get extension path: " + extension_path);
    //     }
    // }

    // //icon image node as string
    // function icon(icon_name){
    //     let icon_path = extension_path+"/icon/"+icon_name;
    //     return ch_img_node_str(icon_path);
    // }


    // update extra network tab pages' cards
    // * replace "replace preview" text button into an icon
    // * add 3 button to each card:
    //  - open model url 🌐
    //  - add trigger words 💡
    //  - use preview image's prompt 🏷️
    // notice: javascript can not get response from python side
    // so, these buttons just sent request to python
    // then, python side gonna open url and update prompt text box, without telling js side.
    function update_card_for_civitai(){

        //css
        let btn_margin = "0px 5px";
        let btn_fontSize = "200%";
        let btn_thumb_fontSize = "100%";
        let btn_thumb_display = "inline";
        let btn_thumb_pos = "static";
        let btn_thumb_backgroundImage = "none";
        let btn_thumb_background = "rgba(0, 0, 0, 0.8)";

        let ch_btn_txts = ['🌐', '💡', '🏷️'];
        let replace_preview_text = getTranslation("replace preview");
        if (!replace_preview_text) {
            replace_preview_text = "replace preview";
        }



        // get component
        let ch_always_display_ckb = gradioApp().querySelector("#ch_always_display_ckb input");
        let ch_show_btn_on_thumb_ckb = gradioApp().querySelector("#ch_show_btn_on_thumb_ckb input");
        let ch_always_display = false;
        let ch_show_btn_on_thumb = false;
        if (ch_always_display_ckb) {
            ch_always_display = ch_always_display_ckb.checked;
        }
        if (ch_show_btn_on_thumb_ckb) {
            ch_show_btn_on_thumb = ch_show_btn_on_thumb_ckb.checked;
        }


        //change all "replace preview" into an icon
        let extra_network_id = "";
        let extra_network_node = null;
        let metadata_button = null;
        let additional_node = null;
        let replace_preview_btn = null;
        let ul_node = null;
        let search_term_node = null;
        let search_term = "";
        let model_type = "";
        let cards = null;
        let is_thumb_mode = false;

        //get current tab
        let active_tab_type = getActiveTabType();
        if (!active_tab_type) {active_tab_type = "txt2img";}

        for (const tab_prefix of tab_prefix_list) {
            if (tab_prefix != active_tab_type) {continue;}


            //find out current selected model type tab
            let active_extra_tab_type = "";
            let extra_tabs = gradioApp().getElementById(tab_prefix+"_extra_tabs");
            if (!extra_tabs) {console.log("can not find extra_tabs: " + tab_prefix+"_extra_tabs");}

            //get active extratab
            const active_extra_tab = Array.from(get_uiCurrentTabContent().querySelectorAll('.extra-network-cards,.extra-network-thumbs'))
                .find(el => el.closest('.tabitem').style.display === 'block')
                ?.id.match(/^(txt2img|img2img)_(.+)_cards$/)[2];


            console.log("found active tab: " + active_extra_tab);

            switch (active_extra_tab) {
                case "textual_inversion":
                    active_extra_tab_type = "ti";
                    break;
                case "hypernetworks":
                    active_extra_tab_type = "hyper";
                    break;
                case "checkpoints":
                    active_extra_tab_type = "ckp";
                    break;
                case "lora":
                    active_extra_tab_type = "lora";
                    break;
                case "lycoris":
                    active_extra_tab_type = "lycoris";
                    break;
            }


            for (const js_model_type of model_type_list) {
                //get model_type for python side
                switch (js_model_type) {
                    case "textual_inversion":
                        model_type = "ti";
                        break;
                    case "hypernetworks":
                        model_type = "hyper";
                        break;
                    case "checkpoints":
                        model_type = "ckp";
                        break;
                    case "lora":
                        model_type = "lora";
                        break;
                    case "lycoris":
                        model_type = "lycoris";
                        break;
                }

                if (!model_type) {
                    console.log("can not get model_type from: " + js_model_type);
                    continue;
                }


                //only handle current sub-tab
                if (model_type != active_extra_tab_type) {
                    continue;
                }

                console.log("handle active extra tab");


                extra_network_id = tab_prefix+"_"+js_model_type+"_"+cardid_suffix;
                // console.log("searching extra_network_node: " + extra_network_id);
                extra_network_node = gradioApp().getElementById(extra_network_id);

                // check if extr network is under thumbnail mode
                // XXX thumbnail mode removed in sd-webui v1.5.0
                is_thumb_mode = false;
                if (extra_network_node) {
                    if (extra_network_node.className == "extra-network-thumbs") {
                        console.log(extra_network_id + " is in thumbnail mode");
                        is_thumb_mode = true;
                        // if (!ch_show_btn_on_thumb) {continue;}
                    }
                } else {
                    console.log("can not find extra_network_node: " + extra_network_id);
                    continue;
                }
                // console.log("find extra_network_node: " + extra_network_id);

                // get all card nodes
                cards = extra_network_node.querySelectorAll(".card");
                for (let card of cards) {
                    //metadata_buttoncard
                    metadata_button = card.querySelector(".metadata-button");
                    //additional node
                    additional_node = card.querySelector(".actions .additional");
                    //get ul node, which is the parent of all buttons
                    ul_node = card.querySelector(".actions .additional ul");
                    if (ul_node==null) {
                        ul_node = document.createElement("ul");
                        additional_node.appendChild(ul_node);
                    }
                    // replace preview text button
                    replace_preview_btn = card.querySelector(".actions .additional a");
                    if (replace_preview_btn==null) {
                        replace_preview_btn = document.createElement("a");
                        additional_node.appendChild(replace_preview_btn);
                    }
                    if (replace_preview_btn == null) {
                        /*
                         * in sdwebui 1.5, the replace preview button has been
                         * moved to a hard to reach location, so we have to do
                         * quite a lot to get to its functionality.
                         */

                        // waste memory by keeping all of this in scope, per card.
                        let page = active_tab_type;
                        let type = js_model_type;
                        let name = card.dataset.name;

                        // create the replace_preview_btn, as it no longer exists
                        replace_preview_btn = document.createElement("a");

                        // create an event handler to redirect a click to the real replace_preview_button
                        replace_preview_btn.addEventListener("click", function(e) {
                            // we have to create a whole hidden editor window to access preview replace functionality
                            extraNetworksEditUserMetadata(e, page, type, name);

                            // the editor window takes quite some time to populate. What a waste.
                            waitForEditor(page, type, name).then(editor => {
                                // Gather the buttons we need to both replace the preview and close the editor
                                let cancel_button = editor.querySelector('.edit-user-metadata-buttons button:first-of-type');
                                let replace_preview_button = editor.querySelector('.edit-user-metadata-buttons button:nth-of-type(2)');

                                replace_preview_button.click();
                                cancel_button.click();
                            });
                        });
                    }

                    // check thumb mode
                    if (is_thumb_mode) {
                        additional_node.style.display = null;

                        if (!ul_node) {
                            // nothing to do.
                            continue;
                        }

                        if (ch_show_btn_on_thumb) {
                            ul_node.style.background = btn_thumb_background;
                        } else {
                            // console.log("remove existed buttons");
                            // remove existed buttons
                            //reset
                            ul_node.style.background = null;
                            // find all .a child nodes
                            let atags = ul_node.querySelectorAll("a");

                            for (let atag of atags) {
                                //reset display
                                atag.style.display = null;
                                //remove extension's button
                                if (ch_btn_txts.indexOf(atag.textContent)>=0) {
                                    //need to remove
                                    ul_node.removeChild(atag);
                                } else {
                                    //do not remove, just reset
                                    atag.textContent = replace_preview_text;
                                    atag.style.display = null;
                                    atag.style.fontSize = null;
                                    atag.style.position = null;
                                    atag.style.backgroundImage = null;
                                }
                            }

                            //also remove br tag in ul
                            let brtag = ul_node.querySelector("br");
                            if (brtag) {
                                ul_node.removeChild(brtag);
                            }

                        }

                        //just reset and remove nodes, do nothing else
                        continue;

                    } else {
                        // full preview mode
                        if (ch_always_display) {
                            additional_node.style.display = "block";
                        } else {
                            additional_node.style.display = null;
                        }


                        if (!ul_node) {
                            ul_node = document.createElement("ul");
                        } else {
                            // remove br tag
                            let brtag = ul_node.querySelector("br");
                            if (brtag) {
                                ul_node.removeChild(brtag);
                            }
                        }

                    }

                    if (replace_preview_btn) {
                        // change replace preview text button into icon
                        if (replace_preview_btn.textContent !== "🖼️") {
                            ul_node.appendChild(replace_preview_btn);
                            replace_preview_btn.textContent = "🖼️";
                            if (!is_thumb_mode) {
                                replace_preview_btn.style.fontSize = btn_fontSize;
                                replace_preview_btn.style.margin = btn_margin;
                            } else {
                                replace_preview_btn.style.display = btn_thumb_display;
                                replace_preview_btn.style.fontSize = btn_thumb_fontSize;
                                replace_preview_btn.style.position = btn_thumb_pos;
                                replace_preview_btn.style.backgroundImage = btn_thumb_backgroundImage;
                            }
                        }
                    }

                    if (ul_node.querySelector('.openurl')) {
                        continue;
                    }

                    // search_term node
                    // search_term = subfolder path + model name + ext
                    search_term_node = card.querySelector(".actions .additional .search_term");
                    if (!search_term_node){
                        console.log("can not find search_term node for cards in " + extra_network_id);
                        continue;
                    }

                    // get search_term
                    search_term = search_term_node.textContent;
                    if (!search_term) {
                        console.log("search_term is empty for cards in " + extra_network_id);
                        continue;
                    }

                    // if (is_thumb_mode) {
                    //     ul_node.style.background = btn_thumb_background;
                    // }

                    // then we need to add 3 buttons to each ul node:
                    let open_url_node = document.createElement("a");
                    open_url_node.href = "#";
                    open_url_node.textContent = "🌐";
                    open_url_node.className = "openurl";
                    if (!is_thumb_mode) {
                        open_url_node.style.fontSize = btn_fontSize;
                        open_url_node.style.margin = btn_margin;
                    } else {
                        open_url_node.style.display = btn_thumb_display;
                        open_url_node.style.fontSize = btn_thumb_fontSize;
                        open_url_node.style.position = btn_thumb_pos;
                        open_url_node.style.backgroundImage = btn_thumb_backgroundImage;
                    }
                    open_url_node.title = "Open this model's civitai url";
                    open_url_node.setAttribute("onclick","open_model_url(event, '"+model_type+"', '"+search_term+"')");

                    let add_trigger_words_node = document.createElement("a");
                    add_trigger_words_node.href = "#";
                    add_trigger_words_node.textContent = "💡";
                    add_trigger_words_node.className = "addtriggerwords";
                    if (!is_thumb_mode) {
                        add_trigger_words_node.style.fontSize = btn_fontSize;
                        add_trigger_words_node.style.margin = btn_margin;
                    } else {
                        add_trigger_words_node.style.display = btn_thumb_display;
                        add_trigger_words_node.style.fontSize = btn_thumb_fontSize;
                        add_trigger_words_node.style.position = btn_thumb_pos;
                        add_trigger_words_node.style.backgroundImage = btn_thumb_backgroundImage;
                    }

                    add_trigger_words_node.title = "Add trigger words to prompt";
                    add_trigger_words_node.setAttribute("onclick","add_trigger_words(event, '"+model_type+"', '"+search_term+"')");

                    let use_preview_prompt_node = document.createElement("a");
                    use_preview_prompt_node.href = "#";
                    use_preview_prompt_node.textContent = "🏷️";
                    use_preview_prompt_node.className = "usepreviewprompt";
                    if (!is_thumb_mode) {
                        use_preview_prompt_node.style.fontSize = btn_fontSize;
                        use_preview_prompt_node.style.margin = btn_margin;
                    } else {
                        use_preview_prompt_node.style.display = btn_thumb_display;
                        use_preview_prompt_node.style.fontSize = btn_thumb_fontSize;
                        use_preview_prompt_node.style.position = btn_thumb_pos;
                        use_preview_prompt_node.style.backgroundImage = btn_thumb_backgroundImage;
                    }
                    use_preview_prompt_node.title = "Use prompt from preview image";
                    use_preview_prompt_node.setAttribute("onclick","use_preview_prompt(event, '"+model_type+"', '"+search_term+"')");

                    //add to card
                    ul_node.appendChild(open_url_node);
                    //add br if metadata_button exists
                    if (is_thumb_mode && metadata_button) {
                        ul_node.appendChild(document.createElement("br"));
                    }
                    ul_node.appendChild(add_trigger_words_node);
                    ul_node.appendChild(use_preview_prompt_node);

                    if (!ul_node.parentElement) {
                        additional_node.appendChild(ul_node);
                    }
                }
            }
        }
    }


    let tab_id = "";
    let extra_tab = null;
    let extra_toolbar = null;
    let extra_network_refresh_btn = null;
    //add refresh button to extra network's toolbar
    for (let prefix of tab_prefix_list) {
        tab_id = prefix + "_extra_tabs";
        extra_tab = gradioApp().getElementById(tab_id);

        //get toolbar
        //get Refresh button
        extra_network_refresh_btn = gradioApp().getElementById(prefix+"_extra_refresh");


        if (!extra_network_refresh_btn){
            console.log("can not get extra network refresh button for " + tab_id);
            continue;
        }

        // add refresh button to toolbar
        let ch_refresh = document.createElement("button");
        ch_refresh.textContent = "🔁";
        ch_refresh.title = "Refresh Civitai Helper's additional buttons";
        ch_refresh.className = "lg secondary gradio-button";
        ch_refresh.style.fontSize = "200%";
        ch_refresh.onclick = update_card_for_civitai;

        extra_network_refresh_btn.parentNode.appendChild(ch_refresh);
    }


    //run it once
    update_card_for_civitai();


});



