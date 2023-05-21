import discord
from redbot.core import commands
import asyncio
import io
import glob
import os
import urllib.request
from os import path

import aiohttp
from tiktokapipy.async_api import AsyncTikTokAPI
from tiktokapipy.models.video import Video

directory = "/root/tikdata"

async def save_slideshow(video: Video):
    vf = "\"scale=iw*min(1080/iw\,1920/ih):ih*min(1080/iw\,1920/ih)," \
         "pad=1080:1920:(0-iw)/2:(1920-ih)/2," \
         "format=yuv420p\""

    for i, image_data in enumerate(video.image_post.images):
        url = image_data.image_url.url_list[-1]
        urllib.request.urlretrieve(url, path.join(directory, f"temp_{video.id}_{i:02}.jpg"))

    urllib.request.urlretrieve(video.music.play_url, path.join(directory, f"temp_{video.id}.mp3"))

    command = [
        "ffmpeg",
        "-r 2/5",
        f"-i {directory}/temp_{video.id}_%02d.jpg",
        f"-i {directory}/temp_{video.id}.mp3",
        "-r 30",
        f"-vf {vf}",
        "-acodec copy",
        f"-t {len(video.image_post.images) * 2.5}",
        f"{directory}/temp_{video.id}.mp4",
        "-y"
    ]
    ffmpeg_proc = await asyncio.create_subprocess_shell(
        " ".join(command),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await ffmpeg_proc.communicate()
    generated_files = glob.glob(path.join(directory, f"temp_{video.id}*"))

    if not path.exists(path.join(directory, f"temp_{video.id}.mp4")):
        for file in generated_files:
            os.remove(file)
        raise Exception("Something went wrong with piecing the slideshow together")

    with open(path.join(directory, f"temp_{video.id}.mp4"), "rb") as f:
        ret = io.BytesIO(f.read())

    for file in generated_files:
        os.remove(file)

    return ret

async def save_video(video: Video):
    async with aiohttp.ClientSession() as session:
        async with session.get(video.video.download_addr) as resp:
            return io.BytesIO(await resp.read())

async def download_video(link):
    async with AsyncTikTokAPI() as api:
        video: Video = await api.video(link)
        if video.image_post:
            downloaded = await save_slideshow(video)
        else:
            downloaded = await save_video(video)

        return downloaded

class TikTok(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api = AsyncTikTokAPI()

    @commands.command()
    async def fetchvideo(self, ctx, video_url: str):
        try:
            video_data = await download_video(video_url)
            video_file = discord.File(video_data, filename="tiktok_video.mp4")
            await ctx.send(file=video_file)
        except Exception as e:
            await ctx.send(f"Error fetching video: {e}")
