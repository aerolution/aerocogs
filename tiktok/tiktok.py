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

async def do_something():
    async with AsyncTikTokAPI() as api:
        challenge = await api.challenge(tag_name)
        async for video in challenge.videos:
            link = video(link)
            
directory = "/root/tikdata"

async def save_slideshow(video: Video):
    # this filter makes sure the images are padded to all the same size
    vf = "\"scale=iw*min(1080/iw\,1920/ih):ih*min(1080/iw\,1920/ih)," \
         "pad=1080:1920:(1080-iw)/2:(1920-ih)/2," \
         "format=yuv420p\""

    for i, image_data in enumerate(video.image_post.images):
        url = image_data.image_url.url_list[-1]
        # this step could probably be done with asyncio, but I didn't want to figure out how
        urllib.request.urlretrieve(url, path.join(directory, f"temp_{video.id}_{i:02}.jpg"))

    urllib.request.urlretrieve(video.music.play_url, path.join(directory, f"temp_{video.id}.mp3"))

    # use ffmpeg to join the images and audio
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
        # optional ffmpeg logging step
        # logging.error(stderr.decode("utf-8"))
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

async def download_video():
    async with AsyncTikTokAPI() as api:
        video: Video = await api.video(link)
        if video.image_post:
            downloaded = await save_slideshow(video)
        else:
            downloaded = await save_video(video)

        # do something with the downloaded video (save it, send it, whatever you want).


class TikTok(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api = AsyncTikTokAPI()

    @commands.command()
    async def trending(self, ctx):
        challenge_name = "fyp"
        count = self.api.challenge.video_limit
        challenge_data = await self.api.challenge(challenge_name, count=1)
        video = challenge_data['items'][0]

        async with aiohttp.ClientSession() as session:
            async with session.get(video['video']['download_addr']) as resp:
                video_data = await resp.read()

        video_file = discord.File(io.BytesIO(video_data), filename="trending_tiktok.mp4")

        embed = discord.Embed(title=video['desc'], color=discord.Color.blue())
        embed.set_author(name=f"@{video['author']['unique_id']}", icon_url=video['author']['avatar_thumb'])
        embed.set_footer(text=f"Uploaded on {video['create_time']}")

        await ctx.send(file=video_file, embed=embed)
