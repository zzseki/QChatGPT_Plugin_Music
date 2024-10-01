from pkg.plugin.context import register, handler, BasePlugin, APIHost, EventContext
from pkg.plugin.events import * # 导入事件类
from mirai import Voice,Plain
import os
import requests
from pathlib import Path
import httpx
import logging
import re
import time
from graiax import silkcoder
import shutil
from pydub import AudioSegment


# 注册插件
@register(name="Music", description="get_music", version="0.1", author="zzseki")
class GetMusic(BasePlugin):
    # 插件加载时触发
    def __init__(self, host: APIHost):
        self.token = ""  # 请将这里的'YOUR_TOKEN'替换为你实际获取的token
        self.cookie = ""  # 请将这里的'YOUR_COOKIE'替换为你实际获取的cookie
        self.logger = logging.getLogger(__name__)


    @handler(PersonNormalMessageReceived)
    async def person_normal_message_received(self, ctx: EventContext):
        receive_text = ctx.event.text_message
        MUSIC_PATTERN = re.compile(r"播放音乐：(.+)")
        match = MUSIC_PATTERN.search(receive_text)
        if match:
            music_name = match.group(1)
            id = await self.get_musicid(music_name)
            msg,url = await self.get_music(id)
            self.ap.logger.info(url)
            #self.msg = msg
            #self.url = url
            if url:
                mp3_path = os.path.join(os.path.dirname(__file__), "temp", "temp.mp3")
                wav_path = os.path.join(os.path.dirname(__file__), "temp", "temp.wav")
                flac_path = os.path.join(os.path.dirname(__file__), "temp", "temp.flac")
                if re.search("flac", url):
                    file_type = "flac"
                    save_path = flac_path
                elif re.search("mp3", url):
                    file_type = "mp3"
                    save_path = mp3_path
                else:
                    file_type = "wav"
                    save_path = wav_path
                if await self.download_audio(url, save_path):
                    silk_file = self.convert_to_silk(save_path)
                    ctx.add_return("reply", [Voice(path=str(silk_file))])
                    self.ap.logger.info("播放音乐：" + music_name)
                    ctx.prevent_default()
            else:
                ctx.add_return("reply", [Plain(str(msg))])
                ctx.prevent_default()

    # 当收到群消息时触发
    @handler(GroupNormalMessageReceived)
    async def group_Normal_message_received(self, ctx: EventContext):
        receive_text = ctx.event.text_message
        MUSIC_PATTERN = re.compile(r"播放音乐：(.+)")
        match = MUSIC_PATTERN.search(receive_text)
        if match:
            music_name = match.group(1)
            id = await self.get_musicid(music_name)
            msg, url = await self.get_music(id)
            self.ap.logger.info(url)
            # self.msg = msg
            # self.url = url
            if url:
                mp3_path = os.path.join(os.path.dirname(__file__), "temp", "temp.mp3")
                wav_path = os.path.join(os.path.dirname(__file__), "temp", "temp.wav")
                flac_path = os.path.join(os.path.dirname(__file__), "temp", "temp.flac")
                if re.search("flac", url):
                    file_type = "flac"
                    save_path = flac_path
                elif re.search("mp3", url):
                    file_type = "mp3"
                    save_path = mp3_path
                else:
                    file_type = "wav"
                    save_path = wav_path
                if await self.download_audio(url, save_path):
                    silk_file = self.convert_to_silk(save_path)
                    ctx.add_return("reply", [Voice(path=str(silk_file))])
                    self.ap.logger.info("播放音乐：" + music_name)
                    ctx.prevent_default()
            else:
                ctx.add_return("reply", [Plain(str(msg))])
                ctx.prevent_default()

    

    async def download_audio(self, audio_url, save_path):
        try:
            response = requests.get(audio_url)
            if response.status_code == 200:
                with open(save_path, "wb") as file:
                    file.write(response.content)
                self.ap.logger.info(f"音频文件已成功保存为 '{save_path}'")
                return True
            else:
                self.ap.logger.error(f"下载音频文件失败，状态码: {response.status_code}")
                return False
        except Exception as e:
            self.ap.logger.error(f"下载音频文件发生异常: {str(e)}")
            return False

    def convert_to_silk(self, save_path: str) -> str:
        temp_folder = os.path.join(os.path.dirname(__file__), "temp")
        silk_path = os.path.join(temp_folder, Path(save_path).stem + ".silk")
        wav_path = save_path

        if save_path.endswith(".mp3"):
            self.ap.logger.info(f"正在将 MP3 文件 {save_path} 转换为 WAV")
            wav_path = os.path.join(temp_folder, Path(save_path).stem + ".wav")
            # 将 mp3 转换为 wav
            audio = AudioSegment.from_mp3(save_path)
            audio.export(wav_path, format="wav")
            self.ap.logger.info(f"MP3 文件已成功转换为 WAV 文件 {wav_path}")

        elif save_path.endswith(".flac"):
            self.ap.logger.info(f"正在将 flac 文件 {save_path} 转换为 WAV")
            wav_path = os.path.join(temp_folder, Path(save_path).stem + ".wav")
            # 将 flac 转换为 wav
            audio = AudioSegment.from_file(save_path, format="flac")
            audio.export(wav_path, format="wav")
            self.ap.logger.info(f"flac 文件已成功转换为 WAV 文件 {wav_path}")

        try:
            silkcoder.encode(wav_path, silk_path)
            self.ap.logger.info(f"已将 WAV 文件 {wav_path} 转换为 SILK 文件 {silk_path}")
            return silk_path
        except Exception as e:
            self.ap.logger.error(f"SILK 文件转换失败: {str(e)}")
            return None

    async def get_music(self, keyword):
        url = "https://v2.alapi.cn/api/music/url"
        params = {
            "id": keyword,
            "format": "json",
            "token": self.token,
            'cookie':self.cookie,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()["data"]
            msg = response.json()["msg"]
            if data:
                url = data["url"]
                return msg, url
            else:
                url = None
                return msg, url

     
    async def get_musicid(self, keyword):
        url = "https://v2.alapi.cn/api/music/search"
        params = {
            "keyword": keyword,
            "token": self.token,
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()["data"]
                first_song = data['songs'][0]['id']
                return first_song
            except httpx.HTTPStatusError as e:
                self.logger.error(f"获取音乐 id 失败: {str(e)}")
                return None

        # 插件卸载时触发
    def __del__(self):
        if hasattr(self, 'folder_path'):
            shutil.rmtree(self.folder_path)


