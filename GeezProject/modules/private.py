# Daisyxmusic (Telegram bot project )
# Copyright (C) 2021  Inukaasith

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

import logging
from GeezProject.modules.msg import Messages as tr
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from GeezProject.config import SOURCE_CODE,ASSISTANT_NAME,PROJECT_NAME,SUPPORT_GROUP,UPDATES_CHANNEL,BOT_USERNAME, OWNER
logging.basicConfig(level=logging.INFO)

@Client.on_message(
    filters.command("start")
    & filters.private
    & ~ filters.edited
)
async def start_(client: Client, message: Message):
    await message.reply_text(
        f"""<b>ʜᴀʟʟᴏ ᴀɴᴀᴋ ʏᴀᴛɪᴍ **{message.from_user.first_name}**\n
ᴋᴇɴᴀʟɪɴ ɢᴜᴀ {PROJECT_NAME}, ɢᴜᴀ ʙɪsᴀ ᴍᴜᴛᴇʀɪɴ ʟᴀɢᴜ ᴅɪ ᴠᴄɢ ʟᴜ,
ɢᴜᴀ ᴘᴜɴʏᴀ ʙᴀɴʏᴀᴋ ꜰɪᴛᴜʀ sᴇᴘᴇʀᴛɪ:
╔════════════════════════════════════╗
 • ᴍᴜᴛᴇʀɪɴ ᴍᴜsɪᴋ ᴅɪ ᴠᴄɢ ʟᴜ
 • ᴅᴏᴡɴʟᴏᴀᴅ ʟᴀɢᴜ ʏᴀɴɢ ʟᴜ ᴍᴀᴜ
 • ᴄᴀʀɪ ʙᴇʀʙᴀɢᴀɪ ᴍᴀᴄᴀᴍ ʟᴀɢᴜ ᴅɪ sᴇʟᴜʀᴜʜ ᴘᴇɴᴊᴜʀᴜ ᴅᴜɴɪᴀ
 • ᴅᴀɴ ʙᴀɴʏᴀᴋ ʟᴀɢɪ.
╚════════════════════════════════════╝
ᴘᴀᴋᴇ ᴘᴇʀɪɴᴛᴀʜ » /help « ʙɪᴀʀ ᴛᴀᴜ ꜰɪᴛᴜʀ ʟᴇɴɢᴋᴀᴘɴʏᴀ!

┏━━━━━━━━━━━━━❂❂━━━━━━━━━━━━━┓
 📌 Makasih udh bikin gua : {OWNER}
┗━━━━━━━━━━━━━❂❂━━━━━━━━━━━━━┛

𝙼𝚊𝚞 𝚖𝚊𝚔𝚎 𝚐𝚞𝚊 𝚋𝚞𝚊𝚝 𝚖𝚞𝚝𝚎𝚛𝚒𝚗 𝚕𝚊𝚐𝚞 𝚍𝚒 𝚐𝚌 𝚕𝚞? 𝙿𝚊𝚔𝚎 𝚊𝚓𝚊, 𝚐𝚞𝚊 𝚐𝚛𝚊𝚝𝚒𝚜 𝚋𝚞𝚊𝚝 𝚠𝚊𝚛𝚐𝚊 𝚝𝚎𝚕𝚎𝚐𝚛𝚊𝚖!
</b>""",

# Edit Yang Seharusnya Lu Edit Aja:D
# Tapi Jangan di Hapus Special Thanks To nya Yaaa :'D

        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "➕ ᴍᴀsᴜᴋɪɴ ɢᴜᴀ ᴋᴇ ɢᴄ ʟᴜ ➕", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")],
                [
                    InlineKeyboardButton(
                        "📢 ᴄʜᴀɴɴᴇʟ ɪɴꜰᴏʀᴍᴀsɪ", url=f"https://t.me/{UPDATES_CHANNEL}"), 
                    InlineKeyboardButton(
                        "⚔️ ɢʀᴏᴜᴘs sᴜᴘᴘᴏʀᴛ", url=f"https://t.me/{SUPPORT_GROUP}")
                ],[
                    InlineKeyboardButton(
                        "💌 ɪɴsᴛᴀɢʀᴀᴍ", url=f"https://instagram.com/fatur.285")
                ],[
                    InlineKeyboardButton(
                        "🛠 sᴏᴜʀᴄᴇ ᴄᴏᴅᴇ 🛠", url=f"https://{SOURCE_CODE}")
                ],[
                    InlineKeyboardButton(
                        "💳 ᴅᴏɴᴀsɪ", url=f"https://t.me/uurfavboys1")
                ]
            ]
        ),
        reply_to_message_id=message.message_id
        )

@Client.on_message(filters.private & filters.incoming & filters.command(['help']))
def _help(client, message):
    client.send_message(chat_id = message.chat.id,
        text = tr.HELP_MSG[1],
        parse_mode="markdown",
        disable_web_page_preview=True,
        disable_notification=True,
        reply_markup = InlineKeyboardMarkup(map(1)),
        reply_to_message_id = message.message_id
    )

help_callback_filter = filters.create(lambda _, __, query: query.data.startswith('help+'))

@Client.on_callback_query(help_callback_filter)
def help_answer(client, callback_query):
    chat_id = callback_query.from_user.id
    disable_web_page_preview=True
    message_id = callback_query.message.message_id
    msg = int(callback_query.data.split('+')[1])
    client.edit_message_text(chat_id=chat_id,    message_id=message_id,
        text=tr.HELP_MSG[msg],    reply_markup=InlineKeyboardMarkup(map(msg))
    )


def map(pos):
    if(pos==1):
        button = [
            [InlineKeyboardButton(text = 'Next »', callback_data = "help+2")]
        ]
    elif(pos==len(tr.HELP_MSG)-1):
        url = f"https://t.me/{SUPPORT_GROUP}"
        button = [
            [InlineKeyboardButton("➕ ᴍᴀsᴜᴋɪɴ ɢᴜᴀ ᴋᴇ ɢᴄ ʟᴜ ➕", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")],
            [InlineKeyboardButton(text = '📢 ᴄʜᴀɴɴᴇʟ ɪɴꜰᴏʀᴍᴀsɪ', url=f"https://t.me/{UPDATES_CHANNEL}"),
             InlineKeyboardButton(text = '⚔️ ɢʀᴏᴜᴘ sᴜᴘᴘᴏʀᴛ', url=f"https://t.me/{SUPPORT_GROUP}")],
            [InlineKeyboardButton(text = '🛠 sᴏᴜʀᴄᴇ ᴄᴏᴅᴇ 🛠', url=f"https://{SOURCE_CODE}")],
            [InlineKeyboardButton(text = '«', callback_data = f"help+{pos-1}")]
        ]
    else:
        button = [
            [
                InlineKeyboardButton(text = '«', callback_data = f"help+{pos-1}"),
                InlineKeyboardButton(text = '»', callback_data = f"help+{pos+1}")
            ],
        ]
    return button


@Client.on_message(
    filters.command("start")
    & filters.group
    & ~ filters.edited
)
async def start(client: Client, message: Message):
    await message.reply_text(
        "🧐 **Lu mau nyari link YouTube?**",
        reply_markup=InlineKeyboardMarkup(
            [   
                [    
                    InlineKeyboardButton(
                        "✅ Y", switch_inline_query_current_chat=""
                    ),
                    InlineKeyboardButton(
                        "❌ G ", callback_data="close"
                    )
                ]
            ]
        )
    )


@Client.on_message(
    filters.command("help")
    & filters.group
    & ~ filters.edited
)
async def help(client: Client, message: Message):
    await message.reply_text(
        """**ᴛᴇᴋᴇɴ ᴛᴏᴍʙᴏʟ ᴅɪ ʙᴀᴡᴀʜ ɪɴɪ ʙɪᴀʀ ʟᴜ ᴛᴀᴜ ᴄᴀʀᴀ ᴍᴀᴋᴇ ɢᴜᴀ**""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📜 ᴄᴀʀᴀ ᴍᴀᴋᴇ ɢᴜᴀ 📜", url="https://telegra.ph/CCARA-PAKE-FANDA-MUSIC-BOT-09-30"
                    )
                ]
            ]
        ),
    )  


@Client.on_message(
    filters.command("reload")
    & filters.group
    & ~ filters.edited
)
async def reload(client: Client, message: Message):
    await message.reply_text("""✅ Bot **udah dimulai ulang!**\n\n• **Daftar etmin** udah **di perbarui y nyet**\n\n• ᴊᴀɴɢᴀɴ sᴘᴀᴍ ʀᴇǫ ᴀᴛᴀᴜ ʟᴀɢᴜ sᴀʏᴀɴɢ... ꜰᴀɴᴅᴀ ᴜᴅᴀʜ ᴛᴏʙᴀᴛ ɢᴀ ᴇɴᴛᴏᴋsɪs ʟᴀɢɪ 😁\n\n• ᴄᴜᴍᴀɴ ᴍᴀᴜ ʙɪʟᴀɴɢ **Dior** ɢᴀɴᴛᴇɴɢ.""",
      reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "ᴊᴏɪɴ ɢᴄ ɢᴜᴀ", url=f"https://t.me/fandaproject"
                    ),
                    InlineKeyboardButton(
                        "ᴛᴜᴀɴ ᴅɪᴏʀ", url=f"https://t.me/uurfavboys1"
                    )
                ]
            ]
        )
   )

