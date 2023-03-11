### Language
[中文](README.cn.md)

# Notice
After updating to new version, you need to shutdown SD webui and re-launch. Just Reload UI won't work!

# Stable-Diffusion-Webui-Civitai-Helper
Stable Diffusion Webui Extension for Civitai, to handle your models much more easily.

Civitai: [Civitai Url](https://civitai.com/models/16768/civitai-helper-sd-webui-civitai-extension)  

# Features
* Scans all models to download model information and preview images from Civitai.  
* Link 1 model to a civitai model by civitai model's url
* Checking all your local model's new version from civitai
* Modified Built-in "Extra Network" cards, to add the following buttons on each card:
  - 🖼: Modified "replace preview" text into this icon
  - 🌐: Open this model's Civitai url in a new tab
  - 💡: Add this model's trigger words to prompt
  - 🏷: Use this model's preview image's prompt


# Install
Go to SD webui's extension tab, go to `Install from url` sub-tab.
Copy this project's url into it, click install.

Alternatively, download this project as a zip file, and unzip it to `Your SD webui folder/extensions`.

Then reload UI with "Reload UI" Button in Setting tab.

Done.

# How to Use
## Update Your SD Webui
This extension need to get extra network's cards id. **Which is added to SD webui since 2023-02-06.** 

So, if you are using a version earlier than this, you need to update your SD Webui! 

## Scanning Models
Go to extension tab "Civitai Helper". There is a button called "Scan model".  

![](img/extension_tab.jpg)

Click it and the extension will scan all your models to generate SHA256 hashes, using them to retreive model information and preview images from Civitai.

**Scanning takes time, just wait it finish**

For each model, it will create a json file to save all model info from Civitai. This model info file will be "Your_model_name.civitai.info" in your model folder.

![](img/model_info_file.jpg)

If a model info file already exists, it will be skipped. If a model cannot be found in Civitai, it will create an empty model info file, so the model won't be scanned twice.

### Adding New Models
When you have some new models, just click scan button again, to get new model's information and preview images. It won't scan the same model twice. 

## Model Card
**(Use this only after scanning finished)** 
Open SD webui's build-in "Extra Network" tab, to show model cards.

![](img/extra_network.jpg)


Move your mouse on to the bottom of a model card. It will show 4 icon buttons:
  - 🖼: Modified "replace preview" text into this icon
  - 🌐: Open this model's Civitai url in a new tab
  - 💡: Add this model's trigger words to prompt
  - 🏷: Use this model's preview image's prompt

![](img/model_card.jpg)

**If these additional buttons are not there**, click the `Refresh Civitai Helper` button to bring them back.  

![](img/refresh_ch.jpg)  
Everytime after Extra Network tab refreshed, it will remove all these additional buttons. So, you need to click `Refresh Civitai Helper` button to bring them back.  

## Get 1 Model Info By Url
If a model's SHA256 can not be found in civitai, but you still want to link it to a civitai model. You can choose this model from list, then offer a civitai model page's url you want to link.   

After clicking button, extension will download that civitai model's model info for this local model file you picked.  

![](img/get_one_model_info.jpg)  


## Checking Model's New Version
You can checking your local model's new version from civitai by model types. You can select multiple model types.   
![](img/check_model_new_version.jpg)  

The checking process has a "1 second delay" after each model's new version checking request. So it is a little slow. 

This is to protect Civitai from facing issue like DDos from this extension. Some cloud service provider has a rule as "no more than 1 API request in a second for free user". Civitai doesn't have this rule yet, but we still need to protect it. There is no good for us if it is down.  

**After checking process done**, it will display all new version's information on UI.  

There are 2 urls for each new version. First one is model's page. Second one is this version's download url.  

![](img/check_model_new_version_output.jpg)


## Preview Image
Extra network uses both `model_file.png` and `model_file.preview.png` as preview image. But `model_file.png` has higher priority, because it is created by yourself.  

When you don't have the higher priority one, it will use the other automatically.  

## Prompt
When you click the button "Use prompt from preview image", it does not use the prompt from your own preview image. It uses the one from civitai's  preview image.  

On civitai, a model's preview images may not has prompt. This extension will check this model's all civitai preview images' information and use the first one has prompt in it.  

## SHA256
To create a file SHA256, it need to read the whole file to generate a hash code. It gonna be slow for big files. 

Default, it uses a Memory Optimized SHA256 which won't stuck your system.(It is the only choice in latest version). So, do not uncheck it if you want to use your computer when scanning.  

There are 2 cases this hash code can not find the model on civitai:
* Some old models, which do not have SHA256 code on civitai.
* The model's owner changed file on civitai, but does not change version number and description. So, the file on civitai is actually not the one on your manchine.  

In these cases, you can always link a model to civitai by filling its URL in this extension.


## Civitai down
When Civitai is facing some issue like DDos, it gonna put civitai under Cloudflare's protection, which gonna re-direct our API request to a real human checking page. Then this extension can not get any information back.  

In that case, juse wait for civitai's recovering. It could take 6-8 hours.  

Enjoy!


# Change Log
## v1.5
* Addtional button now works on thumbnail mode
* Add option to always show addtion button, for touch screen.
* Download a model by model page's url into SD webui's model folder
* Display checking new version's result as gallery and download new version into SD Webui's model folder

## v1.4.2
* ignore .vae file in model folder when scanning

## v1.4.1
* When checking new versions, also searching and ignore already existed ones.
* Add version number to the bottom of this extension's tab

## v1.4
* Support checking model's new version, display the result in UI and offer download url
* Remove addintional sub tabs on extension tab. make ui simpler.

## v1.3
* Open url at client side
* Link selected model to civitai by url or model id
* Save and load extension setting to file
* Show button action's output to UI
* Code refactoring

## v1.2.1
* Add more error checking to work with different versions of SD webui. 

## v1.2
* Support customer model folder
* Support readable model info file
* Support download preview image with max size
* Remove card buttons when extra network is in thumbnail mode

## v1.1
* Support subfolders
* Check if refresh is needed when clicking "Refresh Civitai Helper"
* Add space when adding trigger words
* Add memory Optimized sha256 as an option
