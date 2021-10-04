# Daisyxmusic (Telegram bot project)
# Copyright (C) 2021  Inukaasith
# Copyright (C) 2021  TheHamkerCat (Python_ARQ)
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import json
import os
from os import path
from typing import Callable

import aiofiles
import aiohttp
import ffmpeg
import requests
import wget
from PIL import Image, ImageDraw, ImageFont
from pyrogram import Client, filters
from pyrogram.types import Voice
from pyrogram.errors import UserAlreadyParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from Python_ARQ import ARQ
from youtube_search import YoutubeSearch

from GeezProject.config import ARQ_API_KEY
from GeezProject.config import BOT_NAME as bn
from GeezProject.config import DURATION_LIMIT
from GeezProject.config import UPDATES_CHANNEL as updateschannel
from GeezProject.config import que
from GeezProject.config import SOURCE_CODE,ASSISTANT_NAME,PROJECT_NAME,SUPPORT_GROUP,BOT_USERNAME, OWNER
from GeezProject.function.admins import admins as a
from GeezProject.helpers.admins import get_administrators
from GeezProject.helpers.channelmusic import get_chat_id
from GeezProject.helpers.errors import DurationLimitError
from GeezProject.helpers.decorators import errors
from GeezProject.helpers.decorators import authorized_users_only
from GeezProject.helpers.filters import command, other_filters
from GeezProject.helpers.gets import get_file_name
from GeezProject.services.callsmusic import callsmusic
from GeezProject.services.callsmusic.callsmusic import client as USER
from GeezProject.services.converter.converter import convert
from GeezProject.services.downloaders import youtube
from GeezProject.services.queues import queues

aiohttpsession = aiohttp.ClientSession()
chat_id = None
arq = ARQ("https://thearq.tech", ARQ_API_KEY, aiohttpsession)
DISABLED_GROUPS = []
useer ="NaN"
def cb_admin_check(func: Callable) -> Callable:
    async def decorator(client, cb):
        admemes = a.get(cb.message.chat.id)
        if cb.from_user.id in admemes:
            return await func(client, cb)
        else:
            await cb.answer("Lu kaga diizinin jelek!", show_alert=True)
            return

    return decorator


def transcode(filename):
    ffmpeg.input(filename).output(
        "input.raw", format="s16le", acodec="pcm_s16le", ac=2, ar="48k"
    ).overwrite_output().run()
    os.remove(filename)


# Convert seconds to mm:ss
def convert_seconds(seconds):
    seconds = seconds % (24 * 3600)
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%02d:%02d" % (minutes, seconds)


# Convert hh:mm:ss to seconds
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(":"))))


# Change image size
def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage


async def generate_cover(requested_by, title, views, duration, thumbnail):
    async with aiohttp.ClientSession() as session:
        async with session.get(thumbnail) as resp:
            if resp.status == 200:
                f = await aiofiles.open("background.png", mode="wb")
                await f.write(await resp.read())
                await f.close()

    image1 = Image.open("./background.png")
    image2 = Image.open("./etc/foreground.png")
    image3 = changeImageSize(1280, 720, image1)
    image4 = changeImageSize(1280, 720, image2)
    image5 = image3.convert("RGBA")
    image6 = image4.convert("RGBA")
    Image.alpha_composite(image5, image6).save("temp.png")
    img = Image.open("temp.png")
    img.save("final.png")
    os.remove("temp.png")
    os.remove("background.png")


@Client.on_message(filters.command("playlist") & filters.group & ~filters.edited)
async def playlist(client, message):
    global que
    if message.chat.id in DISABLED_GROUPS:
        return    
    queue = que.get(message.chat.id)
    if not queue:
        await message.reply_text("**Lagi nganggur**")
    temp = []
    for t in queue:
        temp.append(t)
    now_playing = temp[0][0]
    by = temp[0][1].mention(style="md")
    msg = "**Lagu Yang Lagi dimainin** di {}".format(message.chat.title)
    msg += "\n• " + now_playing
    msg += "\n• Req by " + by
    temp.pop(0)
    if temp:
        msg += "\n\n"
        msg += "**Antrian Lagu**"
        for song in temp:
            name = song[0]
            usr = song[1].mention(style="md")
            msg += f"\n• {name}"
            msg += f"\n• Req by {usr}\n"
    await message.reply_text(msg)


# ============================= Settings =========================================


def updated_stats(chat, queue, vol=100):
    if chat.id in callsmusic.pytgcalls.active_calls:
        # if chat.id in active_chats:
        stats = "Pengaturan dari **{}**".format(chat.title)
        if len(que) > 0:
            stats += "\n\n"
            stats += "Volume : {}%\n".format(vol)
            stats += "Lagu dalam antrian : `{}`\n".format(len(que))
            stats += "Sedang memutar lagu : **{}**\n".format(queue[0][0])
            stats += "Requested by : {}".format(queue[0][1].mention)
    else:
        stats = None
    return stats


def r_ply(type_):
    if type_ == "play":
        pass
    else:
        pass
    mar = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⏹", "leave"),
                InlineKeyboardButton("⏸", "puse"),
                InlineKeyboardButton("▶️", "resume"),
                InlineKeyboardButton("⏭", "skip"),
            ],
            [
                InlineKeyboardButton("📖 Playlist", "playlist"),
            ],
            [InlineKeyboardButton("🗑 Keluar be lah", "cls")],
        ]
    )
    return mar


@Client.on_message(filters.command("current") & filters.group & ~filters.edited)
async def ee(client, message):
    if message.chat.id in DISABLED_GROUPS:
        return
    queue = que.get(message.chat.id)
    stats = updated_stats(message.chat, queue)
    if stats:
        await message.reply(stats)
    else:
        await message.reply("**Buka VCG dulu jelek!**")


@Client.on_message(filters.command("player") & filters.group & ~filters.edited)
@authorized_users_only
async def settings(client, message):
    if message.chat.id in DISABLED_GROUPS:
        await message.reply("**Music Player dibunuh**")
        return    
    playing = None
    chat_id = get_chat_id(message.chat)
    if chat_id in callsmusic.pytgcalls.active_calls:
        playing = True
    queue = que.get(chat_id)
    stats = updated_stats(message.chat, queue)
    if stats:
        if playing:
            await message.reply(stats, reply_markup=r_ply("pause"))

        else:
            await message.reply(stats, reply_markup=r_ply("play"))
    else:
        await message.reply("**Buka VCG dulu jelek!**")


@Client.on_message(
    filters.command("musicplayer") & ~filters.edited & ~filters.bot & ~filters.private
)
@authorized_users_only
async def hfmm(_, message):
    global DISABLED_GROUPS
    try:
        user_id = message.from_user.id
    except:
        return
    if len(message.command) != 2:
        await message.reply_text(
            "**Gua cuman kenal sama si** `/musicplayer on` **dan** `/musicplayer off`"
        )
        return
    status = message.text.split(None, 1)[1]
    message.chat.id
    if status == "ON" or status == "on" or status == "On":
        lel = await message.reply("`Processing...`")
        if not message.chat.id in DISABLED_GROUPS:
            await lel.edit("**Pemutar Musik Sudah Diaktifkan Di Obrolan Ini**")
            return
        DISABLED_GROUPS.remove(message.chat.id)
        await lel.edit(
            f"**Pemutar Musik Berhasil Diaktifkan Untuk Pengguna Dalam Obrolan** {message.chat.id}"
        )

    elif status == "OFF" or status == "off" or status == "Off":
        lel = await message.reply("`Processing...`")
        
        if message.chat.id in DISABLED_GROUPS:
            await lel.edit("**Pemutar Musik Sudah dimatikan Dalam Obrolan Ini**")
            return
        DISABLED_GROUPS.append(message.chat.id)
        await lel.edit(
            f"**Pemutar Musik Berhasil Dinonaktifkan Untuk Pengguna Dalam Obrolan** {message.chat.id}"
        )
    else:
        await message.reply_text(
            "**Gua cuman kenal sama si** `/musicplayer on` **dan** `/musicplayer off`"
        )    
        

@Client.on_callback_query(filters.regex(pattern=r"^(playlist)$"))
async def p_cb(b, cb):
    global que
    que.get(cb.message.chat.id)
    type_ = cb.matches[0].group(1)
    cb.message.chat.id
    cb.message.chat
    cb.message.reply_markup.inline_keyboard[1][0].callback_data
    if type_ == "playlist":
        queue = que.get(cb.message.chat.id)
        if not queue:
            await cb.message.edit("**Lagi nganggur bre**")
        temp = []
        for t in queue:
            temp.append(t)
        now_playing = temp[0][0]
        by = temp[0][1].mention(style="md")
        msg = "**Lagu Yang Lagi dimainin** di {}".format(cb.message.chat.title)
        msg += "\n• " + now_playing
        msg += "\n• Req by " + by
        temp.pop(0)
        if temp:
            msg += "\n\n"
            msg += "**Antrian Lagu**"
            for song in temp:
                name = song[0]
                usr = song[1].mention(style="md")
                msg += f"\n• {name}"
                msg += f"\n• Req by {usr}\n"
        await cb.message.edit(msg)


@Client.on_callback_query(
    filters.regex(pattern=r"^(play|pause|skip|leave|puse|resume|menu|cls)$")
)
@cb_admin_check
async def m_cb(b, cb):
    global que
    if (
        cb.message.chat.title.startswith("Channel Music: ")
        and chat.title[14:].isnumeric()
    ):
        chet_id = int(chat.title[13:])
    else:
        chet_id = cb.message.chat.id
    qeue = que.get(chet_id)
    type_ = cb.matches[0].group(1)
    cb.message.chat.id
    m_chat = cb.message.chat

    the_data = cb.message.reply_markup.inline_keyboard[1][0].callback_data
    if type_ == "pause":
        if (chet_id not in callsmusic.pytgcalls.active_calls) or (
            callsmusic.pytgcalls.active_calls[chet_id] == "paused"
        ):
            await cb.answer("Chat is not connected!", show_alert=True)
        else:
            callsmusic.pytgcalls.pause_stream(chet_id)

            await cb.answer("Kok diberentiin sih ngentod!")
            await cb.message.edit(
                updated_stats(m_chat, qeue), reply_markup=r_ply("play")
            )

    elif type_ == "play":
        if (chet_id not in callsmusic.pytgcalls.active_calls) or (
            callsmusic.pytgcalls.active_calls[chet_id] == "playing"
        ):
            await cb.answer("Chat is not connected!", show_alert=True)
        else:
            callsmusic.pytgcalls.resume_stream(chet_id)
            await cb.answer("OKE, LANJOOTTT!!!")
            await cb.message.edit(
                updated_stats(m_chat, qeue), reply_markup=r_ply("pause")
            )

    elif type_ == "playlist":
        queue = que.get(cb.message.chat.id)
        if not queue:
            await cb.message.edit("Player is idle")
        temp = []
        for t in queue:
            temp.append(t)
        now_playing = temp[0][0]
        by = temp[0][1].mention(style="md")
        msg = "**Lagu Yang Lagi diputer** di {}".format(cb.message.chat.title)
        msg += "\n• " + now_playing
        msg += "\n• Req by " + by
        temp.pop(0)
        if temp:
            msg += "\n\n"
            msg += "**Antrian Bansos**"
            for song in temp:
                name = song[0]
                usr = song[1].mention(style="md")
                msg += f"\n• {name}"
                msg += f"\n• Req by {usr}\n"
        await cb.message.edit(msg)

    elif type_ == "resume":
        if (chet_id not in callsmusic.pytgcalls.active_calls) or (
            callsmusic.pytgcalls.active_calls[chet_id] == "playing"
        ):
            await cb.answer("Obrolan tidak terhubung atau sudah diputar", show_alert=True)
        else:
            callsmusic.pytgcalls.resume_stream(chet_id)
            await cb.answer("OKE, LANJOTTT!!!")
    elif type_ == "puse":
        if (chet_id not in callsmusic.pytgcalls.active_calls) or (
            callsmusic.pytgcalls.active_calls[chet_id] == "paused"
        ):
            await cb.answer("Obrolan tidak terhubung atau sudah dijeda", show_alert=True)
        else:
            callsmusic.pytgcalls.pause_stream(chet_id)

            await cb.answer("Kok diberentiin sih ngentod!")
    elif type_ == "cls":
        await cb.answer("Closed menu")
        await cb.message.delete()

    elif type_ == "menu":
        stats = updated_stats(cb.message.chat, qeue)
        await cb.answer("Menu opened")
        marr = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("⏹", "leave"),
                    InlineKeyboardButton("⏸", "puse"),
                    InlineKeyboardButton("▶️", "resume"),
                    InlineKeyboardButton("⏭", "skip"),
                ],
                [
                    InlineKeyboardButton("📖 Daftar putar", "playlist"),
                ],
                [InlineKeyboardButton("🗑️ Keluar be lah", "cls")],
            ]
        )
        await cb.message.edit(stats, reply_markup=marr)
    elif type_ == "skip":
        if qeue:
            qeue.pop(0)
        if chet_id not in callsmusic.pytgcalls.active_calls:
            await cb.answer("Chat is not connected!", show_alert=True)
        else:
            callsmusic.queues.task_done(chet_id)

            if callsmusic.queues.is_empty(chet_id):
                callsmusic.pytgcalls.leave_group_call(chet_id)

                await cb.message.edit("- No More Playlist..\n- Leaving VC!")
            else:
                callsmusic.pytgcalls.change_stream(
                    chet_id, callsmusic.queues.get(chet_id)["file"]
                )
                await cb.answer("Udah gua skip jelek")
                await cb.message.edit((m_chat, qeue), reply_markup=r_ply(the_data))
                await cb.message.reply_text(
                    f"- Skipped track\n- Sekarang muterin **{qeue[0][0]}**"
                )

    else:
        if chet_id in callsmusic.pytgcalls.active_calls:
            try:
                callsmusic.queues.clear(chet_id)
            except QueueEmpty:
                pass

            callsmusic.pytgcalls.leave_group_call(chet_id)
            await cb.message.edit("Successfully Left the Chat!")
        else:
            await cb.answer("Obrolan tidak terhubung!", show_alert=True)


@Client.on_message(command("play") & other_filters)
async def play(_, message: Message):
    global que
    global useer
    if message.chat.id in DISABLED_GROUPS:
        return    
    lel = await message.reply("⏳ **Sabar lagi ngocok**")
    administrators = await get_administrators(message.chat)
    chid = message.chat.id

    try:
        user = await USER.get_me()
    except:
        user.first_name = "FandaProject"
    usar = user
    wew = usar.id
    try:
        # chatdetails = await USER.get_chat(chid)
        await _.get_chat_member(chid, wew)
    except:
        for administrator in administrators:
            if administrator == message.from_user.id:
                if message.chat.title.startswith("Channel Music: "):
                    await lel.edit(
                        f"<b>Ingatlah untuk menambahkan {user.first_name} ke Channel Anda</b>",
                    )
                    pass
                try:
                    invitelink = await _.export_chat_invite_link(chid)
                except:
                    await lel.edit(
                        "<b>Jadiin gua CEO dulu goblok!</b>",
                    )
                    return

                try:
                    await USER.join_chat(invitelink)
                    await USER.send_message(
                        message.chat.id, "**Gua Join Gc Lu Buat Muterin Lagu Di VCG/OS Yeh Anjing, Jangan Dengerin BD Bangsat!**"
                    )
                    await lel.edit(
                        "<b>helper userbot joined your chat</b>",
                    )

                except UserAlreadyParticipant:
                    pass
                except Exception:
                    # print(e)
                    await lel.edit(
                        f"<b>⚙️ Flood Wait Error ⚙️\n{user.first_name} tidak dapat bergabung dengan grup Anda karena banyaknya permintaan bergabung untuk userbot! Pastikan pengguna tidak dibanned dalam grup."
                        f"\n\nAtau tambahkan @{ASSISTANT_NAME} secara manual ke Grup Anda dan coba lagi</b>",
                    )
    try:
        await USER.get_chat(chid)
        # lmoa = await client.get_chat_member(chid,wew)
    except:
        await lel.edit(
            f"<i>{user.first_name} Di banned dari ni gc ngentot, Minta lu admin send perintah `/play` buat pertama kalinya atau tambahin @{ASSISTANT_NAME} secara manual</i>"
        )
        return
    text_links=None
    await lel.edit("🧐 **Mana sih anjing lagunya**")
    if message.reply_to_message:
        entities = []
        toxt = message.reply_to_message.text or message.reply_to_message.caption
        if message.reply_to_message.entities:
            entities = message.reply_to_message.entities + entities
        elif message.reply_to_message.caption_entities:
            entities = message.reply_to_message.entities + entities
        urls = [entity for entity in entities if entity.type == 'url']
        text_links = [
            entity for entity in entities if entity.type == 'text_link'
        ]
    else:
        urls=None
    if text_links:
        urls = True
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    rpk = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"
    audio = (
        (message.reply_to_message.audio or message.reply_to_message.voice)
        if message.reply_to_message
        else None
    )
    if audio:
        if round(audio.duration / 60) > DURATION_LIMIT:
            raise DurationLimitError(
                f"❌ **Lagu dengan durasi lebih dari** `{DURATION_LIMIT}` **menit ga boleh diputer!**"
            )
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("⚔️ Groups", url="https://t.me/MBsokin"),
                    InlineKeyboardButton("📢 Channel", url="https://t.me/diorplayingwords"),
                ],
                [InlineKeyboardButton(text="🚪 Keluar be lah", callback_data="cls")],
            ]
        )
        file_name = get_file_name(audio)
        title = file_name
        thumb_name = "https://telegra.ph/file/a78d27264ba7003f89df2.jpg"
        thumbnail = thumb_name
        duration = round(audio.duration / 60)
        views = "Locally added"
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)
        file_path = await convert(
            (await message.reply_to_message.download(file_name))
            if not path.isfile(path.join("downloads", file_name))
            else file_name
        )
    elif urls:
        query = toxt
        await lel.edit("⏳ **Sabar lagi ngocok**")
        ydl_opts = {"format": "bestaudio[ext=m4a]"}
        try:
            results = YoutubeSearch(query, max_results=1).to_dict()
            url = f"https://youtube.com{results[0]['url_suffix']}"
            # print(results)
            title = results[0]["title"][:25]
            thumbnail = results[0]["thumbnails"][0]
            thumb_name = f"thumb{title}.jpg"
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, "wb").write(thumb.content)
            duration = results[0]["duration"]
            results[0]["url_suffix"]
            views = results[0]["views"]

        except Exception as e:
            await lel.edit(
                "**Busehh ga nemu lagunya.** Cari lagu tuh yang bener lah ngentot, Ketik `/help` kalo butuh bantuan"
            )
            print(str(e))
            return
        dlurl=url
        dlurl=dlurl.replace("youtube","youtubepp")
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("⚔️ Groups", url="https://t.me/MBsokin"),
                    InlineKeyboardButton("📢 Channel", url="https://t.me/diorplayingwords"),
                ],
                [InlineKeyboardButton(text="🚪 Keluar be lah", callback_data="cls")],
            ]
        )
        requested_by = message.from_user.first_name
        await generate_cover(requested_by, title, views, duration, thumbnail)
        file_path = await convert(youtube.download(url))        
    else:
        query = ""
        for i in message.command[1:]:
            query += " " + str(i)
        print(query)
        await lel.edit("⏳ **Sabar lagi ngocok**")
        ydl_opts = {"format": "bestaudio[ext=m4a]"}
        
        try:
          results = YoutubeSearch(query, max_results=5).to_dict()
        except:
          await lel.edit("**Judul lagunya mana ngentod, malesin banget ah!**")
        # Looks like hell. Aren't it?? FUCK OFF
        try:
            toxxt = "**__Pilih lagu yg mau lu puter jelek:__**\n\n"
            j = 0
            useer=user_name
            emojilist = ["⓵","⓶","⓷","⓸","⓹",]

            while j < 5:
                toxxt += f"{emojilist[j]} [{results[j]['title'][:25]}](https://youtube.com{results[j]['url_suffix']})\n"
                toxxt += f" ├ 💡 **Durasi ngentot** - {results[j]['duration']}\n"
                toxxt += f" └ ⚡ __**Powered by** Fanda Project__\n\n"

                j += 1            
            koyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("⓵", callback_data=f'plll 0|{query}|{user_id}'),
                        InlineKeyboardButton("⓶", callback_data=f'plll 1|{query}|{user_id}'),
                        InlineKeyboardButton("⓷", callback_data=f'plll 2|{query}|{user_id}'),
                    ],
                    [
                        InlineKeyboardButton("⓸", callback_data=f'plll 3|{query}|{user_id}'),
                        InlineKeyboardButton("⓹", callback_data=f'plll 4|{query}|{user_id}'),
                    ],
                    [InlineKeyboardButton(text="🚪 Jelek lagunya", callback_data="cls")],
                ]
            )       
            await lel.edit(toxxt,reply_markup=koyboard,disable_web_page_preview=True)
            # WHY PEOPLE ALWAYS LOVE PORN ?? (A point to think)
            return
            # Returning to pornhub
        except:
            await lel.edit("**Tidak ada hasil yang cukup untuk dipilih.. Mulai bermain langsung..**")
                        
            # print(results)
            try:
                url = f"https://youtube.com{results[0]['url_suffix']}"
                title = results[0]["title"][:25]
                thumbnail = results[0]["thumbnails"][0]
                thumb_name = f"thumb{title}.jpg"
                thumb = requests.get(thumbnail, allow_redirects=True)
                open(thumb_name, "wb").write(thumb.content)
                duration = results[0]["duration"]
                results[0]["url_suffix"]
                views = results[0]["views"]

            except Exception as e:
                await lel.edit(
                "**Busehh ga nemu lagunya.** Cari lagu tuh yang bener lah ngentot, Ketik `/help` bila butuh bantuan"
            )
                print(str(e))
                return
            dlurl=url
            dlurl=dlurl.replace("youtube","youtubepp")
            keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("⚔️ Groups", url="https://t.me/MBsokin"),
                    InlineKeyboardButton("📢 Channel", url="https://t.me/diorplayingwords"),
                ],
                [
                    InlineKeyboardButton("🐼ᴅɪᴏʀ ʟᴀɢɪ ᴄᴀʀɪ sʟɪᴘᴋᴏʟᴀɴ", url="https://t.me/uurfavboys1"),
                ],
                [InlineKeyboardButton(text="🚪 Keluar be lah", callback_data="cls")],
            ]
        )
            requested_by = message.from_user.first_name
            await generate_cover(requested_by, title, views, duration, thumbnail)
            file_path = await convert(youtube.download(url))   
    chat_id = get_chat_id(message.chat)
    if chat_id in callsmusic.pytgcalls.active_calls:
        position = await queues.put(chat_id, file=file_path)
        qeue = que.get(chat_id)
        s_name = title
        r_by = message.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        await message.reply_photo(
            photo="final.png",
            caption = f"🏷 **Judul:** [{title[:30]}]({url})\n🕒 **Durasi:** {duration}\n💡 **Status:** Antrian bansos Ke `{position}`\n" \
                    + f"🎵 **Permintaan si kontol ini:** {message.from_user.mention}",
                   reply_markup=keyboard)
       
    else:
        chat_id = get_chat_id(message.chat)
        que[chat_id] = []
        qeue = que.get(chat_id)
        s_name = title
        r_by = message.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        try:
            callsmusic.pytgcalls.join_group_call(chat_id, file_path)
        except:
            message.reply("**VCG nya mana ngentod, Lu kata gua setan muterin lagu ga pake vcg tolol**")
            return
        await message.reply_photo(
            photo="final.png",
            caption = f"🏷 **Judul:** [{title[:30]}]({url})\n🕒 **Durasi:** {duration}\n💡 **Status:** Lagi muterin lagu\n" \
                    + f"🎵 **Permintaan si kontol ini:** {message.from_user.mention}",
                   reply_markup=keyboard)

    os.remove("final.png")
    return await lel.delete()


@Client.on_message(filters.command("ytplay") & filters.group & ~filters.edited)
async def ytplay(_, message: Message):
    global que
    if message.chat.id in DISABLED_GROUPS:
        return
    lel = await message.reply("⏳ **Sabar lagi ngocok**")
    administrators = await get_administrators(message.chat)
    chid = message.chat.id

    try:
        user = await USER.get_me()
    except:
        user.first_name = "FandaProject"
    usar = user
    wew = usar.id
    try:
        # chatdetails = await USER.get_chat(chid)
        await _.get_chat_member(chid, wew)
    except:
        for administrator in administrators:
            if administrator == message.from_user.id:
                if message.chat.title.startswith("Channel Music: "):
                    await lel.edit(
                        f"<b>Ingatlah untuk menambahkan {user.first_name} ke Channel Anda</b>",
                    )
                    pass
                try:
                    invitelink = await _.export_chat_invite_link(chid)
                except:
                    await lel.edit(
                        "<b>Jadiin gua CEO dulu</b>",
                    )
                    return

                try:
                    await USER.join_chat(invitelink)
                    await USER.send_message(
                        message.chat.id, "**Gua Join Gc Lu Buat Muterin Lagu Di VCG/OS Yeh Anjing, Jangan Dengerin BD Bangsat!!**"
                    )
                    await lel.edit(
                        "<b>helper userbot joined your chat</b>",
                    )

                except UserAlreadyParticipant:
                    pass
                except Exception:
                    # print(e)
                    await lel.edit(
                        f"<b>Flood Wait Error\n{user.first_name} tidak dapat bergabung dengan grup Anda karena banyaknya permintaan bergabung untuk userbot! Pastikan pengguna tidak dibanned dalam grup."
                        f"\n\nAtau tambahkan @{ASSISTANT_NAME} secara manual ke Grup Anda dan coba lagi</b>",
                    )
    try:
        await USER.get_chat(chid)
        # lmoa = await client.get_chat_member(chid,wew)
    except:
        await lel.edit(
            f"<i>{user.first_name} dibanned dari ni gc bego, Minta admin lu buat send perintah `/play` buat pertama kalinya atau tambahin @{ASSISTANT_NAME} secara manual</i>"
        )
        return
    await lel.edit("🧐 **mana sih anjing lagunya**")
    user_id = message.from_user.id
    user_name = message.from_user.first_name
     

    query = ""
    for i in message.command[1:]:
        query += " " + str(i)
    print(query)
    await lel.edit("⏳ **Sabar lagi ngocok**")
    ydl_opts = {"format": "bestaudio[ext=m4a]"}
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        url = f"https://youtube.com{results[0]['url_suffix']}"
        # print(results)
        title = results[0]["title"][:25]
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f"thumb{title}.jpg"
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, "wb").write(thumb.content)
        duration = results[0]["duration"]
        results[0]["url_suffix"]
        views = results[0]["views"]

    except Exception as e:
        await lel.edit(
            "**Busehh ga nemu lagunya.** Coba cari dengan judul lagu yang lebih jelas, Ketik `/help` bila butuh bantuan"
        )
        print(str(e))
        return
    dlurl=url
    dlurl=dlurl.replace("youtube","youtubepp")
    keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("⚔️ Groups", url="https://t.me/MBsokin"),
                    InlineKeyboardButton("📢 Channel", url="https://t.me/diorplayingwords"),
                ],
                [
                    InlineKeyboardButton("🐼ᴅɪᴏʀ ʟᴀɢɪ ᴄᴀʀɪ sʟɪᴘᴋᴏʟᴀɴ", url="https://t.me/uurfavboys1"),
                ],
                [InlineKeyboardButton(text="🚪 Keluar be lah", callback_data="cls")],
            ]
        )
    requested_by = message.from_user.first_name
    await generate_cover(requested_by, title, views, duration, thumbnail)
    file_path = await convert(youtube.download(url))
    chat_id = get_chat_id(message.chat)
    if chat_id in callsmusic.pytgcalls.active_calls:
        position = await queues.put(chat_id, file=file_path)
        qeue = que.get(chat_id)
        s_name = title
        r_by = message.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        await message.reply_photo(
            photo="final.png",
            caption = f"🏷 **Judul:** [{title[:30]}]({url})\n🕒 **Durasi:** {duration}\n💡 **Status:** antrian bansos Ke `{position}`\n" \
                    + f"🎵 **Permintaan si kontol ini:** {message.from_user.mention}",
                   reply_markup=keyboard,
        )
        os.remove("final.png")
        return await lel.delete()
    else:
        chat_id = get_chat_id(message.chat)
        que[chat_id] = []
        qeue = que.get(chat_id)
        s_name = title
        r_by = message.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        try:
            callsmusic.pytgcalls.join_group_call(chat_id, file_path)
        except:
            message.reply("**VCG nya mana ngentod, Lu kata gua setan muterin lagu ga ada VCG malesin ah**")
            return
        await message.reply_photo(
            photo="final.png",
            caption = f"🏷 **Judul:** [{title[:30]}]({url})\n🕒 **Durasi:** {duration}\n💡 **Status:** Lagi muter\n" \
                    + f"🎵 **Permintaan si kontol ini:** {message.from_user.mention}",
                   reply_markup=keyboard,)
        os.remove("final.png")
        return await lel.delete()
    

@Client.on_message(filters.command("dplay") & filters.group & ~filters.edited)
async def deezer(client: Client, message_: Message):
    if message_.chat.id in DISABLED_GROUPS:
        return
    global que
    lel = await message_.reply("⏳ **Sabar lagi ngocok**")
    administrators = await get_administrators(message_.chat)
    chid = message_.chat.id
    try:
        user = await USER.get_me()
    except:
        user.first_name = "FandaProject"
    usar = user
    wew = usar.id
    try:
        # chatdetails = await USER.get_chat(chid)
        await client.get_chat_member(chid, wew)
    except:
        for administrator in administrators:
            if administrator == message_.from_user.id:
                if message_.chat.title.startswith("Channel Music: "):
                    await lel.edit(
                        f"<b>Ingatlah untuk menambahkan {user.first_name} ke Channel Anda</b>",
                    )
                    pass
                try:
                    invitelink = await client.export_chat_invite_link(chid)
                except:
                    await lel.edit(
                        "<b>Jadiin Gua CEO ya ngentot!</b>",
                    )
                    return

                try:
                    await USER.join_chat(invitelink)
                    await USER.send_message(
                        message_.chat.id, "Gua Join Gc Lu Buat Muterin Lagu Di VCG/OS Yeh Anjing, Jangan Dengerin BD Bangsat!!!"
                    )
                    await lel.edit(
                        "<b>helper userbot joined your chat</b>",
                    )

                except UserAlreadyParticipant:
                    pass
                except Exception:
                    # print(e)
                    await lel.edit(
                        f"<b>⚙️ Flood Wait Error ⚙️\n{user.first_name} tidak dapat bergabung dengan grup Anda karena banyaknya permintaan bergabung untuk userbot! Pastikan pengguna tidak dibanned dalam grup."
                        f"\n\nAtau tambahkan @{ASSISTANT_NAME} secara manual ke Grup Anda dan coba lagi</b>",
                    )
    try:
        await USER.get_chat(chid)
        # lmoa = await client.get_chat_member(chid,wew)
    except:
        await lel.edit(
            f"<i>{user.first_name} dibanned dari ni gc, Minta admin lu send perintah `/play` buat pertama kalinya atau tambahin @{ASSISTANT_NAME} secara manual</i>"
        )
        return
    requested_by = message_.from_user.first_name

    text = message_.text.split(" ", 1)
    queryy = text[1]
    query = queryy
    res = lel
    await res.edit(f"**Lagi nyari lagu** `{query}` **dari deezer**")
    try:
        songs = await arq.deezer(query,1)
        if not songs.ok:
            await message_.reply_text(songs.result)
            return
        title = songs.result[0].title
        url = songs.result[0].url
        artist = songs.result[0].artist
        duration = songs.result[0].duration
        thumbnail = "https://telegra.ph/file/a78d27264ba7003f89df2.jpg"

    except:
        await res.edit("**Lagu apaansi kok ga ketemu?**")
        return
    try:    
        duuration= round(duration / 60)
        if duuration > DURATION_LIMIT:
            await cb.message.edit(f"**Musik lebih lama dari** `{DURATION_LIMIT}` **menit tidak diperbolehkan diputar**")
            return
    except:
        pass    
    
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(text="📢 Channel", url="https://t.me/fandaproject")],
        ]
    )
    file_path = await convert(wget.download(url))
    await res.edit("📥 **Generating Thumbnail**")
    await generate_cover(requested_by, title, artist, duration, thumbnail)
    chat_id = get_chat_id(message_.chat)
    if chat_id in callsmusic.pytgcalls.active_calls:
        await res.edit("adding in queue")
        position = await queues.put(chat_id, file=file_path)
        qeue = que.get(chat_id)
        s_name = title
        r_by = message_.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        await res.edit_text(f"🗂️ **Lagu yg lu minta lagi ngantri bansos di posisi** `{position}`")
    else:
        await res.edit_text(f"🎶 **Mabar...**")

        que[chat_id] = []
        qeue = que.get(chat_id)
        s_name = title
        r_by = message_.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        try:
            callsmusic.pytgcalls.join_group_call(chat_id, file_path)
        except:
            res.edit("VCG nya mana ngentod, Lu kata gua setan muterin lagu ga ada VCG malesin ah")
            return

    await res.delete()

    m = await client.send_photo(
        chat_id=message_.chat.id,
        reply_markup=keyboard,
        photo="final.png",
        caption=f"🎛️ **Lagi muterin lagu** [{title}]({url}) **Via Deezer**",
    )
    os.remove("final.png")


@Client.on_callback_query(filters.regex(pattern=r"plll"))
async def lol_cb(b, cb):
    global que

    cbd = cb.data.strip()
    chat_id = cb.message.chat.id
    typed_=cbd.split(None, 1)[1]
    #useer_id = cb.message.reply_to_message.from_user.id
    try:
        x,query,useer_id = typed_.split("|")      
    except:
        await cb.message.edit("Lagu apaansi kok ga ketemu?")
        return
    useer_id = int(useer_id)
    if cb.from_user.id != useer_id:
        await cb.answer("Bukan lu yg request jelek!", show_alert=True)
        return
    await cb.message.edit("**Processing**")
    x=int(x)
    try:
        useer_name = cb.message.reply_to_message.from_user.first_name
    except:
        useer_name = cb.message.from_user.first_name
    
    results = YoutubeSearch(query, max_results=5).to_dict()
    resultss=results[x]["url_suffix"]
    title=results[x]["title"][:25]
    thumbnail=results[x]["thumbnails"][0]
    duration=results[x]["duration"]
    views=results[x]["views"]
    url = f"https://youtube.com{resultss}"
    
    try:    
        duuration= round(duration / 60)
        if duuration > DURATION_LIMIT:
            await cb.message.edit(f"Lagu lebih lama dari {DURATION_LIMIT} menit tidak diperbolehkan diputar")
            return
    except:
        pass
    try:
        thumb_name = f"thumb{title}.jpg"
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, "wb").write(thumb.content)
    except Exception as e:
        print(e)
        return
    dlurl=url
    dlurl=dlurl.replace("youtube","youtubepp")
    keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("⚔️ Groups", url="https://t.me/MBsokin"),
                    InlineKeyboardButton("📢 Channel", url="https://t.me/diorplayingwords"),
                ],
                [
                    InlineKeyboardButton("🐼ᴅɪᴏʀ ʟᴀɢɪ ᴄᴀʀɪ sʟɪᴘᴋᴏʟᴀɴ", url="https://t.me/uurfavboys1"),
                ],
                [InlineKeyboardButton(text="🚪 Keluar be lah", callback_data="cls")],
            ]
        )
    requested_by = useer_name
    await generate_cover(requested_by, title, views, duration, thumbnail)
    file_path = await convert(youtube.download(url))  
    if chat_id in callsmusic.pytgcalls.active_calls:
        position = await queues.put(chat_id, file=file_path)
        qeue = que.get(chat_id)
        s_name = title
        try:
            r_by = cb.message.reply_to_message.from_user
        except:
            r_by = cb.message.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)
        await cb.message.delete()
        await b.send_photo(chat_id,
            photo="final.png",
            caption = f"🏷 **Judul:** [{title[:30]}]({url})\n🕒 **Durasi:** {duration}\n💡 **Status:** Antrian bansos Ke `{position}`\n" \
                    + f"🎵 **Permintaan si kontol ini:** {r_by.mention}",
                   reply_markup=keyboard,
        )
        os.remove("final.png")
        
    else:
        que[chat_id] = []
        qeue = que.get(chat_id)
        s_name = title
        try:
            r_by = cb.message.reply_to_message.from_user
        except:
            r_by = cb.message.from_user
        loc = file_path
        appendable = [s_name, r_by, loc]
        qeue.append(appendable)

        callsmusic.pytgcalls.join_group_call(chat_id, file_path)
        await cb.message.delete()
        await b.send_photo(chat_id,
            photo="final.png",
            caption = f"🏷 **Judul:** [{title[:30]}]({url})\n🕒 **Durasi:** {duration}\n💡 **Status:** Lagi muter\n" \
                    + f"🎵 **Permintaan si kontol ini:** {r_by.mention}",
                    reply_markup=keyboard,
        )
        os.remove("final.png")

# Have u read all. If read RESPECT :-)
