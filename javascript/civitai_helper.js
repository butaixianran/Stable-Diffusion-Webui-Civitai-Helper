"use strict";


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
function open_model_url(event, model_type, search_term){
    console.log("start open_model_url");

    //get hidden components of extension 
    let js_msg_txtbox = gradioApp().querySelector("#ch_js_msg_txtbox textarea");
    let js_open_url_btn = gradioApp().getElementById("ch_js_open_url_btn");


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
    js_msg_txtbox.value = JSON.stringify(msg);
    js_msg_txtbox.dispatchEvent(new Event("input"));

    //click hidden button
    js_open_url_btn.click();

    console.log("end open_model_url");


    event.stopPropagation()
    event.preventDefault()

}

function add_trigger_words(event, model_type, search_term){
    console.log("start add_trigger_words");

    //get hidden components of extension 
    let js_msg_txtbox = gradioApp().querySelector("#ch_js_msg_txtbox textarea");
    let js_add_trigger_words_btn = gradioApp().getElementById("ch_js_add_trigger_words_btn");



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
    let prompt = getActivePrompt();
    msg["prompt"] = prompt.value;

    // fill to msg box
    js_msg_txtbox.value = JSON.stringify(msg);
    js_msg_txtbox.dispatchEvent(new Event("input"));

    //click hidden button
    js_add_trigger_words_btn.click();

    console.log("end add_trigger_words");

    event.stopPropagation()
    event.preventDefault()

    
}

function use_preview_prompt(event, model_type, search_term){
    console.log("start use_preview_prompt");

    //get hidden components of extension 
    let js_msg_txtbox = gradioApp().querySelector("#ch_js_msg_txtbox textarea");
    let js_use_preview_prompt_btn = gradioApp().getElementById("ch_js_use_preview_prompt_btn");



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
    prompt = getActivePrompt();
    msg["prompt"] = prompt.value;

    // get active neg prompt
    let neg_prompt = getActiveNegativePrompt();
    msg["neg_prompt"] = neg_prompt.value;

    // fill to msg box
    js_msg_txtbox.value = JSON.stringify(msg);
    js_msg_txtbox.dispatchEvent(new Event("input"));

    //click hidden button
    js_use_preview_prompt_btn.click();

    console.log("end use_preview_prompt");

    event.stopPropagation()
    event.preventDefault()

}


onUiLoaded(() => {



    // get all extra network tabs
    let tab_prefix_list = ["txt2img", "img2img"];
    let model_type_list = ["textual_inversion", "hypernetworks", "checkpoints", "lora"];
    let cardid_suffix = "cards";

    // update extra network tab pages' cards
    // * replace "replace preview" text button into an icon
    // * add 3 button to each card:
    //  - open model url 🌐
    //  - add trigger words 💡
    //  - use preview image's prompt 🏷
    // notice: javascript can not get response from python side
    // so, these buttons just sent request to python
    // then, python side gonna open url and update prompt text box, without telling js side.
    function update_card_for_civitai(){


        //change all "replace preview" into an icon
        let extra_network_id = "";
        let extra_network_node = null;
        let addtional_nodes = null;
        let replace_preview_btn = null;
        let ul_node = null;
        let search_term_node = null;
        let search_term = "";
        let model_type = "";
        let cards = null;
        let need_to_add_buttons = false;
        for (const tab_prefix of tab_prefix_list) {
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
                }

                if (!model_type) {
                    console.log("can not get model_type from: " + js_model_type);
                    continue;
                }

                extra_network_id = tab_prefix+"_"+js_model_type+"_"+cardid_suffix;
                // console.log("searching extra_network_node: " + extra_network_id);
                extra_network_node = gradioApp().getElementById(extra_network_id);
                if (!extra_network_node) {
                    console.log("can not find extra_network_node: " + extra_network_id);
                    continue;
                }
                // console.log("find extra_network_node: " + extra_network_id);

                // get all card nodes
                cards = extra_network_node.querySelectorAll(".card");
                for (let card of cards) {
                    // replace preview text button into icon
                    replace_preview_btn = card.querySelector(".actions .additional a");
                    if (replace_preview_btn) {
                        if (replace_preview_btn.innerHTML == "replace preview") {
							let additionalDiv = card.querySelector(".actions .additional ul");
                            need_to_add_buttons = true;
                            additionalDiv.innerHTML = '<li><div class="weightAndPrompt"><div><span for="weight">Weight</span><input class="gr-box gr-input gr-text-input weightValueText" type="text" name="weightValue" /></div><div><input class="gr-box gr-input gr-text-input weightValue" name="weight" placeholder="Weight" type="range" /><input class="weightActive" type="checkbox" /></div></div></li><li><div><input type="text" class="gr-box gr-input gr-text-input promptValue" name="prompt" placeholder="Prompt" /><input class="promptActive" type="checkbox" /></div></li><li><a href="#" title="replace preview image with currently selected in gallery" onclick="return saveCardPreview(event, \''+model_type+'\', \''+search_term+'\')" target="_blank">replace preview</a><a class="textright" href="#" title="replace preview image with currently selected in gallery" onclick="return use_preview_prompt(event, \''+model_type+'\', \''+search_term+'\')" target="_blank">save</a></li>';
                        }
                    }

                    if (!need_to_add_buttons) {
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
                    search_term = search_term_node.innerHTML;
                    if (!search_term) {
                        console.log("search_term is empty for cards in " + extra_network_id);
                        continue;
                    }
                }       
            }
        }
    }

    //run it once
    update_card_for_civitai();

    let tab_id = ""
    let extra_tab = null;
    let extra_toolbar = null;
    //add refresh button to extra network's toolbar
    for (let prefix of tab_prefix_list) {
        tab_id = prefix + "_extra_tabs";
        extra_tab = gradioApp().getElementById(tab_id);

        //get toolbar
        extra_toolbar = extra_tab.querySelector("div.flex.border-b-2.flex-wrap");

        if (!extra_toolbar){
            console.log("can not get extra network toolbar for " + tab_id);
            continue;
        }

        // add refresh button to toolbar
        let ch_refresh = document.createElement("button");
        ch_refresh.innerHTML = "Refresh Civitai Helper";
        ch_refresh.title = "Refresh Civitai Helper's model card buttons";
        ch_refresh.className = "gr-button gr-button-lg gr-button-secondary";
        ch_refresh.onclick = update_card_for_civitai;

        extra_toolbar.appendChild(ch_refresh);
    }
});



