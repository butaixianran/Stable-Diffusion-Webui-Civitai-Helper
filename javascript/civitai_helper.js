"use strict";

// send msg to python side by filling a hidden text box
// then will click a button to trigger an action
// msg is an object, not a string, will be stringify in this function
function send_ch_py_msg(msg){
    console.log("run send_ch_py_msg")
    let js_msg_txtbox = gradioApp().querySelector("#ch_js_msg_txtbox textarea");
    if (js_msg_txtbox && msg) {
        // fill to msg box
        js_msg_txtbox.value = JSON.stringify(msg);
		let ev = new Event("input");
		Object.defineProperty(ev, 'target', {writable: false, value: js_msg_txtbox});
        js_msg_txtbox.dispatchEvent(ev);
    }

}

// get msg from python side from a hidden textbox
// normally this is an old msg, need to wait for a new msg
function get_ch_py_msg(){
    console.log("run get_ch_py_msg")
    const py_msg_txtbox = gradioApp().querySelector("#ch_py_msg_txtbox textarea");
    if (py_msg_txtbox && py_msg_txtbox.value) {
        console.log("find py_msg_txtbox");
        console.log("py_msg_txtbox value: ");
        console.log(py_msg_txtbox.value)
        return py_msg_txtbox.value
    } else {
        return ""
    }
}


// get msg from python side from a hidden textbox
// it will try once in every sencond, until it reach the max try times
const get_new_ch_py_msg = (max_count=3) => new Promise((resolve, reject) => {
    console.log("run get_new_ch_py_msg")

    let count = 0;
    let new_msg = "";
    let find_msg = false;
    const interval = setInterval(() => {
        const py_msg_txtbox = gradioApp().querySelector("#ch_py_msg_txtbox textarea");
        count++;

        if (py_msg_txtbox && py_msg_txtbox.value) {
            console.log("find py_msg_txtbox");
            console.log("py_msg_txtbox value: ");
            console.log(py_msg_txtbox.value)

            new_msg = py_msg_txtbox.value
            if (new_msg != "") {
                find_msg=true
            }
        }
		
		let ev = new Event("input");
		Object.defineProperty(ev, 'target', {writable: false, value: py_msg_txtbox});
		
        if (find_msg) {
            //clear msg in both sides
            py_msg_txtbox.value = "";
            py_msg_txtbox.dispatchEvent(ev);

            resolve(new_msg);
            clearInterval(interval);
        } else if (count > max_count) {
            //clear msg in both sides
            py_msg_txtbox.value = "";
            py_msg_txtbox.dispatchEvent(ev);

            reject('could not get response from py');
            clearInterval(interval);
        }

    }, 1000);
})




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

function use_preview_prompt(event, model_type, search_term){
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

function save_lora_config(event, model_type, search_term){
    console.log("start save lora config");

    //get hidden components of extension 
    let js_msg_txtbox = gradioApp().querySelector("#ch_js_msg_txtbox textarea");
    let js_save_lora_configs_btn = gradioApp().getElementById("ch_js_save_lora_configs_btn");



    //msg to python side
    let msg = {
        "action": "",
        "model_type": "",
        "search_term": "",
        "prompt": "",
        "neg_prompt": "",
    }

    msg["action"] = "save_lora_configs";
    msg["model_type"] = model_type;
	msg["search_term"] = search_term;

	let card = event.srcElement.parentElement.parentElement;
	let weightValue = card.querySelector(".weightValueText");
	let promptValue = card.querySelector(".promptValue");
	let promptActive = card.querySelector(".promptActive");

    msg["prompt"] = weightValue.value + ";" + promptValue.value + ";" +promptActive.checked;

    // fill to msg box
    js_msg_txtbox.value = JSON.stringify(msg);
	let ev = new Event("input");
	Object.defineProperty(ev, 'target', {writable: false, value: js_msg_txtbox});
    js_msg_txtbox.dispatchEvent(ev);

    //click hidden button
    js_save_lora_configs_btn.click();

    console.log("end save lora config");

    event.stopPropagation()
    event.preventDefault()

}

function get_card_prompt(search_term_to_find) {
	let extra_network_id = "txt2img_lora_cards";
	let extra_network_node = gradioApp().getElementById(extra_network_id);
	
	let cards = extra_network_node.querySelectorAll(".card");
	let foundCard = null;
	for (let card of cards) {
		
		// search_term node
		// search_term = subfolder path + model name + ext
		let search_term_node = card.querySelector(".actions .additional .search_term");
		if (!search_term_node){
			console.log("can not find search_term node for cards in " + extra_network_id);
			continue;
		}

		// get search_term
		let search_term = search_term_node.innerHTML.replace(/^.*[\\\/]/, '').replace(/\.[^/.]+$/, "");;
		if (!search_term) {
			console.log("search_term is empty for cards in " + extra_network_id);
			continue;
		}

		if (search_term.includes(search_term_to_find)) {
			foundCard = card;
			break;
		}
	}
	if (foundCard) {
		let weightValueInput = foundCard.querySelector(".actions .weightValueText");
		let weightInput = foundCard.querySelector(".actions .weightValue");
		let promptInput = foundCard.querySelector(".actions .promptValue");
		let promptActive = foundCard.querySelector(".actions .promptActive");
		
		let finalPrompt = "";
		let loraPrompt = "<lora:"+search_term_to_find+":";
		loraPrompt += weightValueInput.value;
		loraPrompt += ">";
		finalPrompt += loraPrompt;
		
		if (promptActive.checked && promptInput.value.trim() != "") {
			finalPrompt += ", " + promptInput.value;
		}

		return finalPrompt;
		
	}
	return null;
}


// download model's new version into SD at python side
function ch_dl_model_new_version(event, model_path, version_id, download_url){
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

var re_extranet   =    /<([^:]+:[^:]+):[\d\.]+>/;
var re_extranet_g = /\s+<([^:]+:[^:]+):[\d\.]+>/g;

function tryToRemoveExtraNetworkFromPromptOwn(textarea, text){
    var m = text.match(re_extranet)
    if(! m) return false
	
	var newText = text.replaceAll(m[0], "");
	

    var partToSearch = m[1]
    var replaced = false
    var newTextareaText = textarea.value.replaceAll(re_extranet_g, function(found, index){
        m = found.match(re_extranet);
        if(m[1] == partToSearch){
            replaced = true;
            return ""
        }
        return found;
    })
	
	if (newText != "") {
		newTextareaText = newTextareaText.replaceAll(newText, function(found, index){
			replaced = true;
			return "";
		})
	}

    if(replaced){
        textarea.value = newTextareaText
        return true;
    }

    return false
}

function cardClickedOwn(tabname, textToAdd, allowNegativePrompt){
    var textarea = allowNegativePrompt ? activePromptTextarea[tabname] : gradioApp().querySelector("#" + tabname + "_prompt > label > textarea")

    if(! tryToRemoveExtraNetworkFromPromptOwn(textarea, textToAdd)){
        textarea.value = textarea.value + opts.extra_networks_add_text_separator + textToAdd
    }

    updateInput(textarea)
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
    async function update_card_for_civitai(){

        //css
        let btn_thumb_background = "rgba(0, 0, 0, 0.8)";

        let ch_btn_txts = ['🌐', '💡', '🏷'];
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
        let need_to_add_buttons = false;
        let is_thumb_mode = false;
		let loraTxt2ImgInputDict = {};

		console.log("start load_lora_configs");

		//get hidden components of extension 
		let js_msg_txtbox = gradioApp().querySelector("#ch_js_msg_txtbox textarea");
		//let js_open_url_btn = gradioApp().getElementById("ch_js_open_url_btn");
		let js_load_lora_configs_btn = gradioApp().getElementById("ch_js_load_lora_configs_btn");

		//click hidden button
		js_load_lora_configs_btn.click();

		// stop parent event
		//event.stopPropagation()
		//event.preventDefault()

		//check response msg from python
		let new_py_msg = await get_new_ch_py_msg();
		let lora_confs = JSON.parse(new_py_msg);
		lora_confs = JSON.parse(lora_confs["content"]["lora_configs"]);

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
                // check if extr network is under thumbnail mode
                is_thumb_mode = false
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

                let minValue = gradioApp().querySelector("#ch_min_weight_js_cb input").value;
				let maxValue = gradioApp().querySelector("#ch_max_weight_js_cb input").value;
                // get all card nodes
                cards = extra_network_node.querySelectorAll(".card");
                for (let card of cards) {
                    //metadata_buttoncard
                    metadata_button = card.querySelector(".metadata-button");
                    //additional node
                    additional_node = card.querySelector(".actions .additional");
                    //get ul node, which is the parent of all buttons
                    ul_node = card.querySelector(".actions .additional ul");
                    // replace preview text button
                    replace_preview_btn = card.querySelector(".actions .additional a");

                    // check thumb mode
                    if (is_thumb_mode) {
                        additional_node.style.display = null;

                        if (ch_show_btn_on_thumb) {
                            ul_node.style.background = btn_thumb_background;
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
                                    if (ch_btn_txts.indexOf(atag.innerHTML)>=0) {
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
                        if (ch_always_display) {
                            additional_node.style.display = "block";
                        } else {
                            additional_node.style.display = null;
                        }

                        // remove br tag
                        let brtag = ul_node.querySelector("br");
                        if (brtag) {
                            ul_node.removeChild(brtag);
                        }

                    }

                    // change replace preview text button into icon
                    if (replace_preview_btn) {
                        if (replace_preview_btn.innerHTML == replace_preview_text) {
                            need_to_add_buttons = true;
                            replace_preview_btn.innerHTML = "🖼";
                            if (!is_thumb_mode) {
								replace_preview_btn.className = "linkButton";
                            } else {
								replace_preview_btn.className = "linkButtonThumb";
                            }
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
					
					//get ul node, which is the parent of all buttons
                    ul_node = card.querySelector(".actions .additional ul");
					
					// then we need to add 3 buttons to each ul node:
                    let open_url_node = document.createElement("a");
                    open_url_node.href = "#";
                    open_url_node.innerHTML = "🌐";
                    if (!is_thumb_mode) {
						open_url_node.className = "linkButton";
                    } else {
						open_url_node.className = "linkButtonThumb";
                    }
                    open_url_node.title = "Open this model's civitai url";
                    open_url_node.setAttribute("onclick","open_model_url(event, '"+model_type+"', '"+search_term+"')");

                    let add_trigger_words_node = document.createElement("a");
                    add_trigger_words_node.href = "#";
                    add_trigger_words_node.innerHTML = "💡";
                    if (!is_thumb_mode) {
						add_trigger_words_node.className = "linkButton";
                    } else {
						add_trigger_words_node.className = "linkButtonThumb";
                    }

                    add_trigger_words_node.title = "Add trigger words to prompt";
                    add_trigger_words_node.setAttribute("onclick","add_trigger_words(event, '"+model_type+"', '"+search_term+"')");

                    let use_preview_prompt_node = document.createElement("a");
                    use_preview_prompt_node.href = "#";
                    use_preview_prompt_node.innerHTML = "🏷";
                    if (!is_thumb_mode) {
                        use_preview_prompt_node.className = "linkButton";
                    } else {
						use_preview_prompt_node.className = "linkButtonThumb";
                    }
                    use_preview_prompt_node.title = "Use prompt from preview image";
                    use_preview_prompt_node.setAttribute("onclick","use_preview_prompt(event, '"+model_type+"', '"+search_term+"')");
					
					let button_li = document.createElement("li");
					
					button_li.appendChild(open_url_node);
					button_li.appendChild(add_trigger_words_node);
                    button_li.appendChild(use_preview_prompt_node);
					
					open_url_node.parentNode.insertBefore(replace_preview_btn, open_url_node)
					
					if (model_type == "lora" && !is_thumb_mode) {
						let save_node = document.createElement("a");
						// use_preview_prompt_node.href = "#";
						save_node.innerHTML = "💾";
						if (!is_thumb_mode) {
							save_node.className = "linkButton";
						}
						
						let modelname = search_term.replace(/^.*[\\\/]/, '').replace(/\.[^/.]+$/, "");
						save_node.title = "Save config";
						save_node.setAttribute("onclick","save_lora_config(event, '"+model_type+"', '"+modelname+"')");
						
						button_li.appendChild(save_node);
						
						let jokker_li = document.createElement("li");
						let jokker_li2 = document.createElement("li");
						// TODO: get min max from backend
						jokker_li.innerHTML = '<div class="weightAndPrompt"><div><span for="weight">Weight</span><input class="gr-box gr-input gr-text-input weightValueText" type="text" name="weightValue" /></div><div><input class="gr-box gr-input gr-text-input weightValue" name="weight" placeholder="Weight" type="range" step="0.01" min="'+minValue+'" max="'+maxValue+'" /></div></div>';
					
						jokker_li2.innerHTML = '<div><input type="text" class="gr-box gr-input gr-text-input promptValue" name="prompt" placeholder="Prompt" /><input class="promptActive" type="checkbox" /></div>';
						ul_node.appendChild(jokker_li);
						ul_node.appendChild(jokker_li2);
						
						let nameSpan = card.querySelector(".actions .name");
						let weightValueInput = card.querySelector(".actions .weightValueText");
						let weightInput = card.querySelector(".actions .weightValue");
						let promptInput = card.querySelector(".actions .promptValue");
						let promptActive = card.querySelector(".actions .promptActive");
						let loraCardName = nameSpan.innerHTML;
						if (loraCardName in lora_confs === true) {
							weightValueInput.value = lora_confs[loraCardName]["weight"];
							weightInput.value = lora_confs[loraCardName]["weight"];
							promptInput.value = lora_confs[loraCardName]["prompt"];
							promptActive.checked = lora_confs[loraCardName]["prompt_active"];
						}
						
						if (tab_prefix == tab_prefix_list[0]) {
							loraTxt2ImgInputDict[loraCardName] = {weightInput, weightValueInput, promptInput, promptActive};
						}
						else {
							let oldValueInput = loraTxt2ImgInputDict[loraCardName].weightValueInput;
							let oldInput = loraTxt2ImgInputDict[loraCardName].weightInput;
							let oldPrompt = loraTxt2ImgInputDict[loraCardName].promptInput;
							let oldActive = loraTxt2ImgInputDict[loraCardName].promptActive;
							
							promptActive.onchange = function() {
								oldActive.checked = this.checked;
							}
							oldActive.onchange = function() {
								promptActive.checked = this.checked;
							}
							
							promptInput.onchange = function() {
								oldPrompt.value = this.value;
							}
							promptInput.oninput = function() {
								oldPrompt.value = this.value;
							}
							oldPrompt.onchange = function() {
								promptInput.value = this.value;
							}
							oldPrompt.oninput = function() {
								promptInput.value = this.value;
							}
							
							weightInput.onchange = function() {
								weightValueInput.value = this.value;
								oldValueInput.value = this.value;
								oldInput.value = this.value;
							}
							weightInput.oninput = function() {
								weightValueInput.value = this.value;
								oldValueInput.value = this.value;
								oldInput.value = this.value;
							}
							
							weightValueInput.onchange = function() {
								weightInput.value = this.value;
								oldValueInput.value = this.value;
								oldInput.value = this.value;
							}
							weightValueInput.oninput = function() {
								weightInput.value = this.value;
								oldValueInput.value = this.value;
								oldInput.value = this.value;
							}
							
							oldValueInput.onchange = function() {
								weightInput.value = this.value;
								weightValueInput.value = this.value;
								oldInput.value = this.value;
							}
							oldValueInput.oninput = function() {
								weightInput.value = this.value;
								weightValueInput.value = this.value;
								oldInput.value = this.value;
							}
							oldInput.onchange = function() {
								weightInput.value = this.value;
								weightValueInput.value = this.value;
								oldValueInput.value = this.value;
							}
							oldInput.oninput = function() {
								weightInput.value = this.value;
								weightValueInput.value = this.value;
								oldValueInput.value = this.value;
							}
						}
						
						
						let onclickValue = card.getAttribute('onclick');
						let regex = /\((.*?)\)/;
						
						let found = onclickValue.match(regex)[0];
						
						let splits = found.split(',');
						card.setAttribute('onclick','if (event.target !== this) return; cardClickedOwn'+splits[0]+',get_card_prompt("'+loraCardName+'"),'+splits[2]);
					}

                    //add to card
					if (is_thumb_mode) {
						add_trigger_words_node.parentNode.insertBefore(document.createElement("br"), add_trigger_words_node);
                    }
                    ul_node.appendChild(button_li);
                }
            }
        }
    }


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


    //run it once
    setTimeout(function() { update_card_for_civitai(); }, 1000);
	//update_card_for_civitai();
});



