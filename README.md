## link-tools v1.3工具箱更新：

1、使用OpenAI库，会话更流畅稳定，支持更多厂商（如DeepSeek、腾讯云、阿里云、硅基流动等，其他自测）

2、支持自定义添加API模型，KEY置空为Ollama模式，如需快速配置可修改配置文件config/config_ai.ini后刷新导入

3、优化临时中断对话代码，阻断流式输出，修复短时间中断和执行导致的会话受限问题

4、增加输入内容实时tokens显示，合理控制输入内容长度
![image](https://github.com/user-attachments/assets/0998f74e-0489-4d64-b5c6-52c25813efa7)
![image](https://github.com/user-attachments/assets/d9694840-e264-4f70-9cce-d0ad401ecaab)

其他说明：

1、由于使用了OpenAi库，程序打包后大小暴增，本次更新提供EXE版本并公开源码

```
python源码由python3.7编写：
安装库：
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ 
启动工具箱
python link-tools-v1.3.py
```

2、工具箱尝试采用模块化设计，包含正则、Rolan+、AI+三个模块，代码写得随意，师傅们请见谅

3、感谢师傅们的星星，如果有BUG、有建议，交流学习欢迎师傅们滴滴

![image](https://github.com/user-attachments/assets/3f3dabc2-a8fb-4de5-9c36-979cf0399480)


## link-tools v1.2工具箱更新：

1、Deepseek官方API接口更新，同步新增自定义模型（原deepseek-chat为V3模型，deepseek-reasoner为R1模型）

2、新增工具箱配置，允许自定义修改工具箱首页模块。

3、其他说明：

 -- 由于流式输出，超时功能可能会失效，可自行中止。

 -- 经测试可支持腾讯云API，对应修改key、api、model即可，其他厂商API自行测试。

![image](https://github.com/user-attachments/assets/4b4ad3b0-0f3b-4165-a8b4-c8d7a1721188)
![image](https://github.com/user-attachments/assets/d701ceb7-0878-49f3-8f08-1bbd6f70f718)


## link-tools v1.1工具箱更新：
1、新增AI+模块，支持3种模型连接方式（Deepseek Api、Siliconflow Api和Ollama本地部署接入），目前R1模型的Api不稳定，可以使用V3模型，效果也不错。

2、支持提示词自定义增删查改，可随时中止AI进行修改和完善提示词。

3、内置多条提示词（来自ChinaRan404师傅的DeepSeekSelfTool项目，超强）。

4、AI+模块代码由Deepseek R1生成。

5、Rolan+模块修复已知BUG，去除工具灰色标记代码。

![image](https://github.com/user-attachments/assets/37d669c2-8e1c-4817-b97e-7f6ccf9c0537)
![image](https://github.com/user-attachments/assets/794fe439-8c16-4db0-800c-a07b82a1530e)
![image](https://github.com/user-attachments/assets/ecba6fe9-7c37-444c-9d4c-45cce258308a)

## link-tools工具箱

link-tools为一款Windows GUI界面的渗透测试工具箱（仿rolan启动器），支持拖拉新增工具（脚本、文件夹），支持自定义运行参数和备注，支持bat批量运行脚本，支持RapidScanner端口扫描结果服务指纹联动工具，可协助安全运维人员快速运行工具（脚本、文件夹），提高安全检测效率。
![image](https://github.com/user-attachments/assets/5f12f86c-4527-4b7a-af30-bf3e12f08665)
## 使用方法：

### 1. 工具添加：

**右键新建分组，拖拉新增工具**

#### 1.1 分组栏支持：

- 拖拉排序、刷新、新增、重命名、删除

#### 1.2 工具栏支持：

- 拖拉新增工具（文件夹）、拖拉排序、双击打开、右键打开、打开目录、刷新、新增、重命名、删除、配置文件、移动分组

![image](https://github.com/user-attachments/assets/5e365e08-804e-4e50-be83-58c2281509a7)

### 2. 参数配置：

**点击工具（脚本）激活参数栏，填写工具（脚本）启动参数，保存参数。**

#### 2.1 示例：

python3 tool.py -f [file] -o [log]

python2 tool.py -i [ip] -p [port]

tool.exe -l [target]

#### 2.2 数据参数说明：

[file]： -f [file] ，数据写入一个临时文件，由工具运行

[ip] [port]： -ip [ip] -p [port] ，数据按':'进行分割，并逐行（批量）运行

[target]： -u [target] ，数据无处理，并逐行（批量）运行

[log]： -o [log] ,统一格式和位置：[logpath]/log-[tool_name]-[date].txt（当使用[log]时[输出/日志]按钮打开统一位置，否则为工具所在目录）

[date]：当前时间

[logpath]：统一位置

![image](https://github.com/user-attachments/assets/83bdd62d-f456-4f24-bbe6-765c1e009f98)

### 3. 工具启动

图形化工具：支持双击运行、右键打开运行

脚本工具（带参数）：选择要运行的命令，使用【启动/运行】按钮运行
![image](https://github.com/user-attachments/assets/0f216f9c-a552-4bea-bc42-57caf34f6fde)

### 4. RapidScanner工具联动

支持导入处理RapidScanner扫描结果scan_result.txt数据，并输出处理结果到文件夹

#### 4.1 扫描数据
![image](https://github.com/user-attachments/assets/a789dd9a-9f76-4070-88ef-17a7f5097360)


#### 4.2 导入数据
![image](https://github.com/user-attachments/assets/6bb0895f-9035-4ea6-930b-4f4291f805c5)

**处理后的端口数据保存到result目录下，二次导入数据可使用文件夹方式导入**

![image](https://github.com/user-attachments/assets/39a791b8-cf64-4dc0-9f8e-5abb98ab372f)
#### 4.3 展示数据
![image](https://github.com/user-attachments/assets/588129e6-0479-4024-996c-82ca968cf2b0)


#### 4.4 工具联动
常用工具提前配置**服务类型**，选中数据时**展示工具快捷入口**，点击工具可**快速加载工具启动参数**数据。
![image](https://github.com/user-attachments/assets/63dbe486-ef37-4c0e-8a88-7a2763de8ecc)

### 5. 使用示例

可快速联动各种工具，一键运行，提高效率。
![image](https://github.com/user-attachments/assets/c0ed33cd-adbe-4d88-aa11-42f5328f4a53)

### 6. 正则小工具

支持快速生成和匹配简单正则表达式，处理数据。支持自定义常用表达式，配置文件config/正则.txt
![image](https://github.com/user-attachments/assets/2edf0b44-c516-4b03-a3bd-0c92b477e57b)

## 其他说明：

1、工具名称灰色问题：出于工具箱迁移考虑，非link-tools工具箱目录下的工具标记灰色。

2、工具编写：基于python3.7+pyqt5，启动器通过生成bat方式运行（可脱离工具箱运行），个人编写的小工具，欢迎提出建议。
