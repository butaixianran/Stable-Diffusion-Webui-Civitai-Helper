# Stable-Diffusion-Webui-Civitai-Helper
Stable Diffusion Webui 扩展Civitai助手，用于更轻松的管理和使用Civitai模型。

# 功能
* 扫描所有模型，从Civitai下载模型信息和预览图 
* 修改了内置的"Extra Network"模型卡片，每个卡片增加了如下功能按钮:
  - 🖼: 修改文字"replace preview"为这个图标
  - 🌐: 在新标签页打开这个模型的Civitai页面
  - 💡: 一键添加这个模型的触发词到关键词输入框
  - 🏷: 一键使用这个模型预览图所使用的关键词

# 安装
下载本项目为zip文件，解压到`你的SD webui目录/extensions`下即可。

然后使用设置页面的"Reload UI"按钮重新加载UI。  


# 使用方法
## 扫描模型
前往扩展页面"Civitai Helper"，有个按钮叫："Scan Model"  

![](img/extension_tab.jpg)  

点击，就会扫描所有模型，生成SHA256码，用于从civitai获取模型信息和预览图。  

每个模型，本扩展都会创建一个json文件，用来保存从civitai得到的模型信息。这个文件会保存在模型同目录下，名称为："模型名字.civitai.info"。  

![](img/model_info_file.jpg)  

如果模型信息文件已经存在，扫描时就会跳过这个模型。如果模型不是civitai的，就会创建个空信息文件，以避免以后重复扫描。

### 添加新模型
当你下载了新模型之后，只要再次点击扫描按钮即可。已经扫描过的文件不会重复扫描，会自动得到新模型的信息和预览图。无须重启SD webui。 

## 模型卡片
打开SD webui's 内置的 "Extra Network" 页面，显示模型卡片  

![](img/extra_network.jpg)  


移动鼠标到模型卡片底部，就会显示4个按钮：
  - 🖼: 修改文字"replace preview"为这个图标
  - 🌐: 在新标签页打开这个模型的Civitai页面
  - 💡: 一键添加这个模型的触发词到关键词输入框
  - 🏷: 一键使用这个模型预览图所使用的关键词
  
![](img/model_card.jpg)  

如果你刷新了卡片页面，这些额外的功能按钮就会消失。这时只要点击`Refresh Civitai Helper`，他们就会被重新添加到卡片上。  

![](img/refresh_ch.jpg)  



Enjoy! 





