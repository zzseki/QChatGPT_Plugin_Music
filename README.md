## 安装

配置完成 [QChatGPT](https://github.com/RockChinQ/QChatGPT) 主程序后使用管理员账号向机器人发送命令即可安装：

```
!plugin get <插件发布仓库地址>
```
或查看详细的[插件安装说明](https://github.com/RockChinQ/QChatGPT/wiki/5-%E6%8F%92%E4%BB%B6%E4%BD%BF%E7%94%A8)

## 使用

前往https://www.alapi.cn/  进行注册（截至上传时是免费的）

需要下载安装ffmpeg

Linux可执行如下命令来安装ffmpeg
```
sudo apt install ffmpeg
```

在控制面板左侧——接口管理——更新Token密钥，点击Copy复制Token

在本插件文件夹下main.py文件中找到这行，并替换成你获取到的token（不要弄丢引号）

```
self.token = 'YOURTOKEN'  # 请将这里的'YOUR_TOKEN'替换为你实际获取的token
self.cookie = "YOUR_COOKIE"  # 请将这里的'YOUR_COOKIE'替换为你实际获取的cookie
```

另外main.py中的self.cookie为你网易云音乐的cookie，如果没有请将其设为空，若设为空一些vip歌曲可能只能获取30秒

只能获取网易云音乐上有的音乐


## 注意

如果该插件目录内没有”temp“文件夹需自行创建


## 配置GPT

向QChatGpt发送：播放音乐：XXX(歌名)(空格)XXX(歌手)
也可以不限制歌手

