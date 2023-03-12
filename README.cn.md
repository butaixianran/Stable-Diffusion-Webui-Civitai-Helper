# Stable-Diffusion-Webui-Civitai-Helper
Stable Diffusion Webui 扩展Civitai助手，用于更轻松的管理和使用Civitai模型。

[Civitai Url](https://civitai.com/models/16768/civitai-helper-sd-webui-civitai-extension)  

# 注意
在安装或更新新版本之后，需要整个关闭SD Webui，重新启动它。光是Reload UI对本插件不起作用。  

# 功能
* 扫描所有模型，从Civitai下载模型信息和预览图 
* 通过civitai模型的页面url，连接一个本地模型和civitai模型的信息
* 批量检查本地模型，在civitai上的新版本
* 修改了内置的"Extra Network"模型卡片，每个卡片增加了如下功能按钮:
  - 🖼: 修改文字"replace preview"为这个图标
  - 🌐: 在新标签页打开这个模型的Civitai页面
  - 💡: 一键添加这个模型的触发词到关键词输入框
  - 🏷: 一键使用这个模型预览图所使用的关键词

# 安装
下载本项目为zip文件，解压到`你的SD webui目录/extensions`下即可。

然后使用设置页面的"Reload UI"按钮重新加载UI。  

(不了解git的国内用户，请勿通过SD webui的插件界面安装或升级。  
它安装的时候，是调用你本地的git命令行工具来下载，不是通过浏览器下载。你的git工具没有配置过代理和SSL的话，就会下载失败)  


# 使用方法
## 更新你的SD webui
本扩展需要取到 Extra Network的卡片列表id。**这个是2023-02-06，才添加到SD webui里面的。**  

所以，如果你用的版本比这个早，你就需要先更新你的SD Webui！


## 扫描模型
前往扩展页面"Civitai Helper"，有个按钮叫："Scan Model"  

![](img/extension_tab.jpg)  

点击，就会扫描所有模型，生成SHA256码，用于从civitai获取模型信息和预览图。**扫描需要很久，耐心等待**。

每个模型，本扩展都会创建一个json文件，用来保存从civitai得到的模型信息。这个文件会保存在模型同目录下，名称为："模型名字.civitai.info"。  

![](img/model_info_file.jpg)  

如果模型信息文件已经存在，扫描时就会跳过这个模型。如果模型不是civitai的，就会创建个空信息文件，以避免以后重复扫描。

### 添加新模型
当你下载了新模型之后，只要再次点击扫描按钮即可。已经扫描过的文件不会重复扫描，会自动得到新模型的信息和预览图。无须重启SD webui。 

## 模型卡片
**(先完成扫描，再使用卡片功能)**  
打开SD webui's 内置的 "Extra Network" 页面，显示模型卡片  

![](img/extra_network.jpg)  


移动鼠标到模型卡片底部，就会显示4个按钮：
  - 🖼: 修改文字"replace preview"为这个图标
  - 🌐: 在新标签页打开这个模型的Civitai页面
  - 💡: 一键添加这个模型的触发词到关键词输入框
  - 🏷: 一键使用这个模型预览图所使用的关键词
  
![](img/model_card.jpg)  

如果你没有看到这些额外的按钮，只要点击`Refresh Civitai Helper`，他们就会被重新添加到卡片上。  

![](img/refresh_ch.jpg)  

每次当Extra Network刷新，他都会删除掉额外的修改，我们的按钮就会消失。这时你就需要点击`Refresh Civitai Helper`把这些功能添加回去。


## 根据URL获取1个模型信息
如果无法在civitai上找到你的模型的SHA256，但你还是希望能把你的模型连接到一个civitai模型，你可以在本扩展页面，从列表中选择你的模型，并提供一个civitai模型页面的url。

点击按钮之后，扩展就会下载那个civitai模型的信息，作为你这个本地模型的信息使用。  

![](img/get_one_model_info.jpg)  


## 批量检查模型新版本
你可以按照模型类型，批量检查你的本地模型，在civitai上的新版本。你可以选择多个模型类型。  
![](img/check_model_new_version.jpg)  

检查新版本的时候，每检查完一个模型，都会有一个1秒的延迟，所以速度有点慢。

这是为了保护Civitai避免因为本插件而短暂陷入类似DDos的局面。有些云服务商，有类似“免费用户每秒API请求不能超过1次”的保护机制。Civitai还没有这种设置。但我们还是得自觉保护它。因为如果它挂了，对大家都没有好处。    

**检查完毕之后**，就会如下图，在UI上显示所有找到的新版本的信息。  

每个模型新版本，都有2个链接。第一个是这个模型的网页。第二个是这个新版本的下载地址。   
![](img/check_model_new_version_output.jpg)


## 预览图
Extra Network支持两种预览图命名：`model_name.png` 和 `model_name.preview.png`。其中，`model_name.png`优先级较高。

当优先级较高的预览图不存在，他就会自动使用`model_name.preview.png`。

这样，你自己创建的预览图 和 网络下载的预览图，能够同时存在，并优先使用你自己创建的。

## 关键词
卡片上，添加关键词按钮，是添加从civitai预览图中得到的关键词，而不是你自己创建的图片的关键词。

civitai不是每个图片都有关键词，一个模型中，也不是所有预览图关键词都一样。所以这里是遍历所有civitai预览图信息，加载第一个有关键词的。


## SHA256
为了创建文件的SHA256，插件需要读取整个文件。对于大尺寸文件，就会很慢。

默认，插件使用内存优化的SHA256生成方法，就不会卡住你的系统(最新版本强制使用内存优化的)。所以，如果你想要在扫描模型的同时使用电脑，就不要取消勾选这个优化。  

有两种情况，这个SHA256无法从civitai找到对应模型：
* 太老的模型，civitai没有存储SHA256.
* 模型作者，静静的换掉了模型文件，但没有修改描述和版本。所以，虽然网页上看不出来，但实际上civitai上的 和你本地的模型文件，已经不是同一个文件了。  

这些情况下，你可以在插件上，通过提供模型页面的url，来获取模型信息文件。（v1.3新功能）




## Civitai本身挂掉
Civitai在面临类似DDos的问题的时候，会把整个网站立刻置于Cloudflare验证机制的保护下，包括API的接口。于是，API请求，就会被跳转到Cloudflare的真人验证页面而无法获取任何信息。

这种情况，请耐心等待Civitai恢复之后，再使用需要连接Civitai的功能。根据以往经验，每次Civitai这样折腾一轮要6-8小时。



Enjoy! 





