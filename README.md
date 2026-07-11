
<div align="right">
  <details>
    <summary >🌐 Language</summary>
    <div>
      <div align="center">
        <a href="https://openaitx.github.io/view.html?user=flh155&project=qq-farm-bot-vision&lang=en">English</a>
        | <a href="https://openaitx.github.io/view.html?user=flh155&project=qq-farm-bot-vision&lang=zh-CN">简体中文</a>
        | <a href="https://openaitx.github.io/view.html?user=flh155&project=qq-farm-bot-vision&lang=zh-TW">繁體中文</a>
        | <a href="https://openaitx.github.io/view.html?user=flh155&project=qq-farm-bot-vision&lang=ja">日本語</a>
        | <a href="https://openaitx.github.io/view.html?user=flh155&project=qq-farm-bot-vision&lang=ko">한국어</a>
        | <a href="https://openaitx.github.io/view.html?user=flh155&project=qq-farm-bot-vision&lang=hi">हिन्दी</a>
        | <a href="https://openaitx.github.io/view.html?user=flh155&project=qq-farm-bot-vision&lang=th">ไทย</a>
        | <a href="https://openaitx.github.io/view.html?user=flh155&project=qq-farm-bot-vision&lang=fr">Français</a>
        | <a href="https://openaitx.github.io/view.html?user=flh155&project=qq-farm-bot-vision&lang=de">Deutsch</a>
        | <a href="https://openaitx.github.io/view.html?user=flh155&project=qq-farm-bot-vision&lang=es">Español</a>
        | <a href="https://openaitx.github.io/view.html?user=flh155&project=qq-farm-bot-vision&lang=it">Italiano</a>
        | <a href="https://openaitx.github.io/view.html?user=flh155&project=qq-farm-bot-vision&lang=ru">Русский</a>
        | <a href="https://openaitx.github.io/view.html?user=flh155&project=qq-farm-bot-vision&lang=pt">Português</a>
        | <a href="https://openaitx.github.io/view.html?user=flh155&project=qq-farm-bot-vision&lang=nl">Nederlands</a>
        | <a href="https://openaitx.github.io/view.html?user=flh155&project=qq-farm-bot-vision&lang=pl">Polski</a>
        | <a href="https://openaitx.github.io/view.html?user=flh155&project=qq-farm-bot-vision&lang=ar">العربية</a>
        | <a href="https://openaitx.github.io/view.html?user=flh155&project=qq-farm-bot-vision&lang=fa">فارسی</a>
        | <a href="https://openaitx.github.io/view.html?user=flh155&project=qq-farm-bot-vision&lang=tr">Türkçe</a>
        | <a href="https://openaitx.github.io/view.html?user=flh155&project=qq-farm-bot-vision&lang=vi">Tiếng Việt</a>
        | <a href="https://openaitx.github.io/view.html?user=flh155&project=qq-farm-bot-vision&lang=id">Bahasa Indonesia</a>
        | <a href="https://openaitx.github.io/view.html?user=flh155&project=qq-farm-bot-vision&lang=as">অসমীয়া</
      </div>
    </div>
  </details>
</div>

# qq-farm-bot-vision
# QQ经典农场机器人（AI视觉版本）
## 基于CV视觉匹配的初版已开发完成，Alaph版本已发布，注意：这是早期测试版本，功能不全还在持续开发和优化中，主要是想让部分用户试用一下，协助测试BUG和提意见。
## 最新功能更新日志请查看：[update_cv.txt](./update_cv.txt)
## 试用过程中遇到问题可提issue：[issue问题区](https://github.com/flh155/qq-farm-bot-vision/issues)
## 技术交流可以进Discord：[农民交流频道](https://discord.gg/xbpVKG9wKw)

## 以下是CV版本的部署试用方法
### 备注：因这是测试版本，会存在很多问题以及功能的缺失，因此暂时不提供docker、exe等一键安装部署的方法使用，仅提供源码启动的方式，供一些有一定技术基础且愿意尝鲜的用户试用，后续待版本更新优化的比较完善且稳定后再提供一键部署的方案给大家使用，望理解

## ❗ 用前必读：
- 当前版本要求游戏窗口必须实时保持在前台，但可以被遮挡
- 当前版本已有初版GUI界面，如需使用请启动`python main_gui.py`
- 当前版本已实现`自动收菜`、`自动除草/除虫/浇水`、`自动种植（测试中）`、`自动偷菜`、`自动帮忙除草/除虫/浇水`、`自动领取每日免费化肥` 功能，相关功能在不断测试优化中
- 图像模板匹配可能会因各种因素导致匹配不到或是误匹配情况出现，需要根据使用情况调整相关参数阈值，阈值参数调整方法参考：[threshold_adjust.txt](./threshold_adjust.txt)
- 设置了按键监听便于快捷控制机器人，快捷键：`Ctrl+c`立马停止并退出机器人，`p` 临时暂停/恢复机器人巡检

---
## 分支说明
- ### ~~[silence-click分支](https://github.com/flh155/qq-farm-bot-vision/tree/silence-click)：将点击模式为了静默点击，要求游戏画面仍然在前端，但不会和用户抢鼠标进行点击，注意：这种模式下可能会存在被封号的风险，请各位自行决定是否使用，若使用了希望多观察反馈情况~~ (该分支已合并进main分支)
- ### [gui-pr分支](https://github.com/flh155/qq-farm-bot-vision/tree/gui-pr)：该分支提供给大家进行GUI界面的PR，项目默认GUI界面会比较简单，如果你有好的GUI界面设计，可以提交PR到这个分支（目前该分支暂时无提交）

---
## GUI界面展示
![GUI](./assert/gui.jpg)

## 系统配置要求
- Windows 10及以上的系统（Linux等其它系统还未开发适配）
- 本地已安装Python（推荐使用conda环境），且Python版本 ≥ 3.9
- 已安装NT架构的桌面版QQ，且能打开农场页面
## 部署试用流程方法
- 1、`git clone` 本项目到本地，打开PC版QQ并登录
- 2、在项目根目录下打开终端（可选：切换conda环境），使用命令 `pip install -r requirement.txt` 安装项目运行所需依赖
- 3、检查根目录下 `config.ini` 配置文件，按照个人的需求修改相关配置项参数
- 4、使用命令 `python main.py` 启动机器人，查看终端是否启动成功(GUI界面启动命令为 `python main_gui.py`)
- 5、打开农场游戏窗口（注意当前版本必须保证游戏窗口无遮挡）
- 6、程序会自动控制鼠标点击相关功能按钮实现自动化
---
# 后续研发计划
- ~~初版实现以cv为基础的图像匹配模式实现收菜、驱虫、除草功能（先快速有一个简版给大家过渡使用）~~（已实现）
- ~~加入GUI界面，便于使用~~(已实现)
- 优化丰富CV匹配版本的功能，修复存在的问题（正在进行中）
- 采集画面数据集：清洗处理、标注、增强
- 基于yolo神经网络训练目标检测模型
- 使用神经网络更加精准及丰富地识别各类图标，丰富功能（种菜、收菜、偷菜、种地等）
# 你的star⭐是我更新的动力
---
## 首先非常感谢大家对项目的关注和star⭐，但是因为本人平时在搬砖，只有摸鱼和下班后才有时间更新和维护项目，且本项目又是从零开始的，所以进度会慢一些，代码质量可能会稍微差一些，希望大家能理解，也欢迎各路大神提PR成为项目贡献者，最后相关开发进度我会及时更新，请大家耐心等待

# 免责声明 ❗  
## 本项目仅供大家作为研究、学习和交流AI与计算机视觉技术应用用途，承诺永久开源免费，严禁任何人直接或间接对项目进行二次开发、包装后进行售卖、宣传等非法用途，且使用本项目可能会违反游戏服务条款导致被封号等处罚，若使用本项目代码则视为你已知晓并同意以上信息，由此造成的一切后果由使用者自行承担，与作者无关。