from pkg.plugin.context import register, handler, BasePlugin, APIHost, EventContext
from pkg.plugin.events import (
    NormalMessageResponded,
    PersonMessageReceived,
    GroupMessageReceived,GroupNormalMessageReceived,PersonNormalMessageReceived

)
from mirai import Voice
import os
import requests
from pathlib import Path
import httpx
import logging
import re
import time
from graiax import silkcoder
import shutil


# 注册插件
@register(name="Music", description="get_music", version="0.1", author="zzseki")
class GetMusic(BasePlugin):
    # 插件加载时触发
    def __init__(self, host: APIHost):
        self.token = "YOUR_TOKEN"  # 请将这里的'YOUR_TOKEN'替换为你实际获取的token
        self.logger = logging.getLogger(__name__)
        self.matches = None

    @handler(PersonMessageReceived)
    async def person_message_received(self, ctx: EventContext, **kwargs):
        receive_text = str(ctx.event.message_chain)
        MUSIC_PATTERN = re.compile(r"播放音乐：(.+)")
        match = MUSIC_PATTERN.search(receive_text)
        if match:
            self.matches = match
            music_name = match.group(1)
            id = await self.get_musicid(music_name)
            url = await self.get_music(id)
            save_path = os.path.join(os.path.dirname(__file__), "temp", "temp.wav")
            if await self.download_audio(url, save_path):
                silk_file = self.convert_to_silk(save_path)
                if silk_file:
                    # 可以将结果存储在实例属性中，以便在后续的事件处理器中使用
                    self.silk_file = silk_file  # 假设是实例属性
                    # 如果需要在这里做一些回复或记录，可以在这里完成
                    return  # 这里不需要返回任何东西，事件处理器不应该返回值

    @handler(GroupMessageReceived)
    async def group_message_received(self, ctx: EventContext, **kwargs):
        receive_text = str(ctx.event.message_chain)
        MUSIC_PATTERN = re.compile(r"播放音乐：(.+)")
        match = MUSIC_PATTERN.search(receive_text)
        if match:
            self.matches = match
            music_name = match.group(1)
            id = await self.get_musicid(music_name)
            url = await self.get_music(id)
            save_path = os.path.join(os.path.dirname(__file__), "temp", "temp.wav")
            if await self.download_audio(url, save_path):
                silk_file = self.convert_to_silk(save_path)
                if silk_file:
                    self.silk_file = silk_file
                    return

    @handler(NormalMessageResponded)
    async def normal_message_responded(self, ctx: EventContext, **kwargs):
        if self.matches and hasattr(self, 'silk_file'):
            ctx.add_return("reply", [Voice(path=str(self.silk_file))])
            await ctx.event.query.adapter.reply_message(ctx.event.query.message_event, "为你播放音乐：" + self.matches.group(1))
            self.matches = None


        else:
            self.logger.error("未找到合适的 SILK 文件路径")


    async def download_audio(self, audio_url, save_path):
        try:
            response = requests.get(audio_url)
            if response.status_code == 200:
                with open(save_path, "wb") as file:
                    file.write(response.content)
                self.logger.info(f"音频文件已成功保存为 '{save_path}'")
                return True
            else:
                self.logger.error(f"下载音频文件失败，状态码: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"下载音频文件发生异常: {str(e)}")
            return False

    def convert_to_silk(self, wav_path: str) -> str:
        temp_folder = os.path.join(os.path.dirname(__file__), "temp")
        silk_path = os.path.join(temp_folder, Path(wav_path).stem + ".silk")

        try:
            silkcoder.encode(wav_path, silk_path)
            self.logger.info(f"已将 WAV 文件 {wav_path} 转换为 SILK 文件 {silk_path}")
            return silk_path
        except Exception as e:
            self.logger.error(f"SILK 文件转换失败: {str(e)}")
            return None

    async def get_music(self, keyword):
        url = "https://v2.alapi.cn/api/music/url"
        params = {
            "id": keyword,
            "format": "json",
            "token": self.token,
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()["data"]
                url = data["url"]
                return url
            except httpx.HTTPStatusError as e:
                self.logger.error(f"获取音乐 URL 失败: {str(e)}")
                return None

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


