"use strict";

function ch_convert_file_path_to_url(path) {
    let prefix = "file=";
    let path_to_url = path.replaceAll('\\', '/');
    return prefix + path_to_url;
}

function ch_img_node_str(path) {
    return `<img src='${ch_convert_file_path_to_url(path)}' style="width:24px"/>`;
}

function ch_gradio_version() {
    let foot = gradioApp().getElementById("footer");
    if (!foot) { return null; }

    let versions = foot.querySelector(".versions");
    if (!versions) { return null; }

    if (versions.innerHTML.indexOf("gradio: 3.16.2") > 0) {
        return "3.16.2";
    } else {
        return "3.23.0";
    }
}

// send msg to python side by filling a hidden text box
// then will click a button to trigger an action
// msg is an object, not a string, will be stringify in this function
function send_ch_py_msg(msg) {
    // console.log("run send_ch_py_msg")
    let js_msg_txtbox = gradioApp().querySelector("#ch_js_msg_txtbox textarea");
    if (js_msg_txtbox && msg) {
        // fill to msg box
        js_msg_txtbox.value = JSON.stringify(msg);
        js_msg_txtbox.dispatchEvent(new Event("input"));
    }
}

// get msg from python side from a hidden textbox
// normally this is an old msg, need to wait for a new msg
function get_ch_py_msg() {
    console.log("run get_ch_py_msg")
    const py_msg_txtbox = gradioApp().querySelector("#ch_py_msg_txtbox textarea");
    if (py_msg_txtbox && py_msg_txtbox.value) {
        console.log("find py_msg_txtbox, value:", py_msg_txtbox.value)
        return py_msg_txtbox.value
    } else {
        return ""
    }
}

// get msg from python side from a hidden textbox
// it will try once in every sencond, until it reach the max try times
const get_new_ch_py_msg = (max_count = 7) => new Promise((resolve, reject) => {
    let count = 0;
    let new_msg = "";
    let find_msg = false;
    const interval = setInterval(() => {
        const py_msg_txtbox = gradioApp().querySelector("#ch_py_msg_txtbox textarea");
        count++;

        if (py_msg_txtbox && py_msg_txtbox.value) {
            console.log("find py_msg_txtbox, value: ", py_msg_txtbox.value)
            new_msg = py_msg_txtbox.value
            if (new_msg != "") {
                find_msg = true
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
    }, 400);
})

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

// button's click function
async function open_model_url(event, model_type, search_term) {
    console.log("start open_model_url");

    //get hidden components of extension 
    let js_open_url_btn = gradioApp().getElementById("ch_js_open_url_btn");
    if (!js_open_url_btn) {
        return
    }

    //msg to python side
    let msg = {
        "action": "",
        "model_type": "",
        "search_term": "",
        "prompt": "",
        "neg_prompt": "",
    }

    msg["action"] = "open_url";
    msg["model_type"] = model_type;
    msg["search_term"] = search_term;
    msg["prompt"] = "";
    msg["neg_prompt"] = "";

    // fill to msg box
    send_ch_py_msg(msg)

    //click hidden button
    js_open_url_btn.click();

    // stop parent event
    event.stopPropagation()
    event.preventDefault()

    //check response msg from python
    let new_py_msg = await get_new_ch_py_msg();
    // console.log("new_py_msg:", new_py_msg);

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
    console.log("end open_model_url")
}

function add_trigger_words(event, model_type, search_term) {
    console.log("start add_trigger_words");

    //get hidden components of extension 
    let js_add_trigger_words_btn = gradioApp().getElementById("ch_js_add_trigger_words_btn");
    if (!js_add_trigger_words_btn) {
        return
    }

    //msg to python side
    let msg = {
        "action": "",
        "model_type": "",
        "search_term": "",
        "prompt": "",
        "neg_prompt": "",
    }

    msg["action"] = "add_trigger_words";
    msg["model_type"] = model_type;
    msg["search_term"] = search_term;
    msg["neg_prompt"] = "";

    // get active prompt
    let act_prompt = getActivePrompt();
    msg["prompt"] = act_prompt.value;

    // fill to msg box
    send_ch_py_msg(msg)

    //click hidden button
    js_add_trigger_words_btn.click();
    console.log("end add_trigger_words");

    event.stopPropagation()
    event.preventDefault()
}

function use_preview_prompt(event, model_type, search_term) {
    console.log("start use_preview_prompt");

    //get hidden components of extension 
    let js_use_preview_prompt_btn = gradioApp().getElementById("ch_js_use_preview_prompt_btn");
    if (!js_use_preview_prompt_btn) {
        return
    }

    //msg to python side
    let msg = {
        "action": "",
        "model_type": "",
        "search_term": "",
        "prompt": "",
        "neg_prompt": "",
    }

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
    send_ch_py_msg(msg)

    //click hidden button
    js_use_preview_prompt_btn.click();

    console.log("end use_preview_prompt");

    event.stopPropagation()
    event.preventDefault()
}

async function delete_model(event, model_type, search_term) {
    if (!confirm('Comfirm delete model: "' + search_term + '"?')) { return }

    //get hidden components of extension 
    let js_delete_model_btn = gradioApp().getElementById("ch_js_delete_model_btn");
    if (!js_delete_model_btn) {
        return
    }

    //msg to python side
    let msg = {
        "action": "delete_model",
        "model_type": model_type,
        "search_term": search_term
    }

    // fill to msg box
    send_ch_py_msg(msg)

    //click hidden button
    js_delete_model_btn.click();

    // stop parent event
    event.stopPropagation()
    event.preventDefault()

    //check response msg from python
    let new_py_msg = await get_new_ch_py_msg();
    console.log("new_py_msg:", new_py_msg);

    //check msg
    if (new_py_msg) {
        let py_msg_json = JSON.parse(new_py_msg);
        //check delete result
        console.log(py_msg_json)
        if (py_msg_json && py_msg_json.result) {
            alert('Model delete successfully!!')
            let card = event.target.closest('.card')
            card.parentNode.removeChild(card)
        }
    }
}

// download model's new version into SD at python side
function ch_dl_model_new_version(event, model_path, version_id, download_url) {
    console.log("start ch_dl_model_new_version");

    // must confirm before downloading
    let dl_confirm = "\nConfirm to download.\n\nCheck Download Model Section's log and console log for detail.";
    if (!confirm(dl_confirm)) {
        return
    }

    //get hidden components of extension 
    let js_dl_model_new_version_btn = gradioApp().getElementById("ch_js_dl_model_new_version_btn");
    if (!js_dl_model_new_version_btn) {
        return
    }

    //msg to python side
    let msg = {
        "action": "",
        "model_path": "",
        "version_id": "",
        "download_url": "",
    }

    msg["action"] = "dl_model_new_version";
    msg["model_path"] = model_path;
    msg["version_id"] = version_id;
    msg["download_url"] = download_url;

    // fill to msg box
    send_ch_py_msg(msg)

    //click hidden button
    js_dl_model_new_version_btn.click();

    console.log("end dl_model_new_version");

    event.stopPropagation()
    event.preventDefault()
}

function createAdditionalButton(btnProps) {
    let el = document.createElement("a");
    Object.assign(el, btnProps);
    el.setAttribute('onclick', btnProps.onclick)
    el.className = 'civitai-helper-action'
    el.href = "#";
    return el
}

function convert_to_py_model_type(js_model_type) {
    //get model_type for python side
    switch (js_model_type) {
        case "textual_inversion": return "ti";
        case "hypernetworks": return "hyper";
        case "checkpoints": return "ckp";
        case "lora": return "lora";
        case "lycoris": return "lycoris";
    }
}

// add just one model_type cards buttons
function update_card_for_one_tab(model_type, container) {

    let ch_btn_txts = ['🌐', '💡', '🪞', '🗑️'];
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
    let metadata_button = null;
    let additional_node = null;
    let replace_preview_btn = null;
    let ul_node = null;
    let search_term_node = null;
    let search_term = "";
    let is_thumb_mode = false;

    // check if extr network is under thumbnail mode
    is_thumb_mode = false;
    if (container.className == "extra-network-thumbs") {
        is_thumb_mode = true;
        // if (!ch_show_btn_on_thumb) {continue;}
    }

    model_type = convert_to_py_model_type(model_type);

    for (let card of container.children) {
        //get ul node, which is the parent of all buttons
        ul_node = card.querySelector(".actions .additional ul");

        if (ul_node.childElementCount > 1) {
            // buttons all ready added, just quit
            console.log('buttons all ready added, just quit')
            return
        }

        //metadata_buttoncard
        metadata_button = card.querySelector(".metadata-button");
        //additional node
        additional_node = card.querySelector(".actions .additional");
        // replace preview text button
        replace_preview_btn = card.querySelector(".actions .additional a");

        // check thumb mode
        if (is_thumb_mode) {
            additional_node.style.display = null;

            if (ch_show_btn_on_thumb) {
                ul_node.style.background = "rgba(0, 0, 0, .5)";
            } else {
                //reset
                ul_node.style.background = null;
                // console.log("remove existed buttons");
                // remove existed buttons
                if (ul_node) {
                    // find all .a child nodes
                    let atags = ul_node.querySelectorAll("a");

                    for (let atag of atags) {
                        //reset display
                        atag.style.display = null;
                        //remove extension's button
                        if (ch_btn_txts.indexOf(atag.innerHTML) >= 0) {
                            //need to remove
                            ul_node.removeChild(atag);
                        } else {
                            //do not remove, just reset
                            atag.innerHTML = replace_preview_text;
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
            }

        } else {
            // full preview mode
            additional_node.style.display = ch_always_display ? "block" : null;

            // remove br tag
            let brtag = ul_node.querySelector("br");
            if (brtag) {
                ul_node.removeChild(brtag);
            }
        }

        // change replace preview text button into icon
        if (replace_preview_btn) {
            replace_preview_btn.className = "civitai-helper-action";
            replace_preview_btn.innerHTML = "🖼️";
        }

        // search_term node
        // search_term = subfolder path + model name + ext
        search_term_node = card.querySelector(".actions .additional .search_term");
        if (!search_term_node) {
            console.log("can not find search_term node for cards in " + extra_network_id);
            continue;
        }

        // get search_term
        search_term = search_term_node.innerText;
        if (!search_term) {
            console.log("search_term is empty for cards in " + extra_network_id);
            continue;
        }
        // remove webui added extra checkpoint's sha256 value, 
        // in file: stable-diffusion-webui/modules/ui_extra_networks_checkpoints.py
        // line: 24: "search_term": self.search_terms_from_path(checkpoint.filename) + " " + (checkpoint.sha256 or ""),
        search_term = search_term.split(" ")[0];

        // if (is_thumb_mode) {
        //     ul_node.style.background = btn_thumb_background;
        // }

        // then we need to add 4 buttons to each ul node:
        let open_url_node = createAdditionalButton({
            innerHTML: "🌐",
            title: "Open this model's civitai url",
            onclick: "open_model_url(event, '" + model_type + "', '" + search_term + "')"
        })

        let add_trigger_words_node = createAdditionalButton({
            innerHTML: "💡",
            title: "Add trigger words to prompt",
            onclick: "add_trigger_words(event, '" + model_type + "', '" + search_term + "')"
        })

        let use_preview_prompt_node = createAdditionalButton({
            innerHTML: "🪞",
            title: "Use prompt from preview image",
            onclick: "use_preview_prompt(event, '" + model_type + "', '" + search_term + "')"
        })

        let delete_model_node = createAdditionalButton({
            innerHTML: "🗑️",
            title: "Delete model",
            onclick: "delete_model(event, '" + model_type + "', '" + search_term + "')",
        })

        //add to card
        ul_node.appendChild(open_url_node);
        //add br if metadata_button exists
        if (is_thumb_mode && metadata_button) {
            ul_node.appendChild(document.createElement("br"));
        }
        ul_node.appendChild(add_trigger_words_node);
        ul_node.appendChild(use_preview_prompt_node);
        ul_node.appendChild(delete_model_node);
    }
}

// fast pasete civitai model url and trigger model info loading
async function checkClipboard() {
    let text = await navigator.clipboard.readText()
    if (text.startsWith('https://civitai.com/models/')) {
        let comp = document.querySelector('#model_download_url_txt')
        let textarea = comp.querySelector('textarea')
        textarea.value = text
        textarea.dispatchEvent(new Event('input'))
        comp.querySelector('button').click()
    }
}

// shotcut key event listener
window.addEventListener('keydown', e => {
    let el = e.target
    switch (e.key) {
        case '`':
            if (el.isContentEditable || el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') { e.preventDefault() }
            let type = getActiveTabType()
            if (type.endsWith('2img')) {
                document.querySelector('#' + type + '_extra_networks')?.click()
            }
            break
        case 'x':
            let txt = document.querySelector('#quicksettings + .tabs button.selected').innerText
            if (txt == 'Civitai Helper')
                checkClipboard()
            else if (txt.endsWith('2img') && e.altKey)
                document.querySelector(`button#${txt}_generate`).click()
            break
    }
})


onUiLoaded(() => {

    //get gradio version
    let gradio_ver = ch_gradio_version();
    console.log("gradio_ver:" + gradio_ver);

    let tab_prefix_list = ["txt2img", "img2img"];
    let model_type_list = ["textual_inversion", "hypernetworks", "checkpoints", "lora", "lycoris"];

    // add all model_type cards buttons by tab_prefix
    function update_card_form_all_tab(tab_prefix) {
        for (let model_type of model_type_list) {
            let container_id = [tab_prefix, model_type, 'cards'].join('_')
            let container = document.getElementById(container_id)
            update_card_for_one_tab(model_type, container);
        }
    }

    // get init py msg
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

    // // icon image node as string
    // function icon(icon_name){
    //     let icon_path = extension_path+"/icon/"+icon_name;
    //     return ch_img_node_str(icon_path);
    // }

    // check cards number change, and re-craete buttons
    function checkPeriodically(tab_prefix, model_type) {
        let container_id = '#' + [tab_prefix, model_type, 'cards_html'].join('_')
        let container = document.querySelector(container_id + ' ' + container_id)

        // record current cards size
        let len = container.querySelectorAll('.card').length

        // we only wait 5s, after that we assumed that DOM will never changed
        let millis = 1000 * 5

        // wait for server response and DOM updates, if cards size changed, 
        // then our buttons is losted, put them back again
        let timer = setInterval(() => {
            let new_len = container.querySelectorAll('.card').length
            if (len != new_len) {
                update_card_for_one_tab(model_type, container.lastElementChild)
                clearInterval(timer)
            }
            millis -= 500
            if (millis <= 0) {
                clearInterval(timer)
            }
        }, 500)
    }

    let tab_id = ""
    let extra_tab = null;
    let extra_toolbar = null;
    let extra_network_refresh_btn = null;
    // add refresh button to extra network's toolbar
    for (let tab_prefix of tab_prefix_list) {
        tab_id = tab_prefix + "_extra_tabs";
        extra_tab = gradioApp().getElementById(tab_id);

        //get toolbar
        //get Refresh button
        extra_network_refresh_btn = gradioApp().getElementById(tab_prefix + "_extra_refresh");

        if (!extra_network_refresh_btn) {
            console.log("can not get extra network refresh button for " + tab_id);
            continue;
        }

        // add refresh button to toolbar
        let ch_refresh = document.createElement("button");
        ch_refresh.innerHTML = "🔄️";
        ch_refresh.title = "Refresh Civitai Helper's additional buttons";
        ch_refresh.className = "lg secondary gradio-button";
        ch_refresh.style.fontSize = "2em";
        ch_refresh.onclick = () => update_card_form_all_tab(tab_prefix)

        extra_network_refresh_btn.parentNode.appendChild(ch_refresh);

        // listen to refresh buttons' click event
        // check and re-add buttons back on
        document.getElementById(tab_prefix + '_extra_refresh').addEventListener('click', e => {
            let model_type = e.target.closest('.tab-nav').querySelector('button.selected').innerText.replaceAll(' ', '_').toLowerCase()
            checkPeriodically(tab_prefix, model_type)
        })

        // listen to "Extra Networks" toggle button's click event,
        // then initialiy add all buttons, only trigger once,
        // after that all updates are trigger by refresh button click.
        document.getElementById(tab_prefix + '_extra_networks').addEventListener('click', () => {
            // wait UI updates
            setTimeout(() => update_card_form_all_tab(tab_prefix), 1500);
        }, { once: true })
    }

});