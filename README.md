罗技鼠标专用
=====

1. 导入游戏配置文件

2. 进入游戏之后启动 Auto.exe

罗技lua脚本使用的kiccer大佬提供的 https://github.com/kiccer/Soldier76.git

##### 作者QQ:434461000

原理如下

每秒截图游戏中一号武器位 跟资源图片对比

~~控制键盘 CAPSLOCK NUMLOCK SCRLKLOCK 键盘状态~~

~~Soldier76脚本 修改代码判断状态达到自动切换武器~~

现在利用lua dofile读取文件变量（默认配置文件路径为D:\config.lua）


如果有更好的方式 可以联系作者

实测资源占用 

i9 CPU 0.4% 

~~内存占用不超过100MB~~ 200M左右

# 该分支为本人魔改版本，设备支持 2K屏，罗技G102(lua脚本请使用LGS驱动)，
  侧键前键为满配压枪（装备红点枪补三角或者消焰拇指，消炎红握把，也可无枪口只装直角握把）
  侧键后键为无配件压枪
  DPI键为停止压枪
  数字键5投掷物模式不压枪
  自动识别站姿与蹲姿
  支持红点全息SHIFT键放大射击，倍镜模式
  可使用F1关闭自动识别，F2~F7手动绑定枪械至1号位或2号位（参考文件resource/keyboard_dict.json）。
  暂不支持配件识别
  

# 免责申明

***使用此软件可能造成账号被封禁 作者概不承担责任 使用此软件自动接受此条款***

***使用此软件可能造成账号被封禁 作者概不承担责任 使用此软件自动接受此条款***

***使用此软件可能造成账号被封禁 作者概不承担责任 使用此软件自动接受此条款***
