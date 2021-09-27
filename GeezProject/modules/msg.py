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

import os
from GeezProject.config import SOURCE_CODE,ASSISTANT_NAME,PROJECT_NAME,SUPPORT_GROUP,UPDATES_CHANNEL, OWNER
class Messages():
      HELP_MSG = [
        ".",
f"""
**Anjay lu lagi, welcome back di {PROJECT_NAME}

✣️ {PROJECT_NAME} bisa muterin musik di VCG lu tanpa ribet.

✣️ Assisten Music » @{ASSISTANT_NAME}\n\nTeken Next buat lanjutin**

""",

f"""
**Pengaturan**

1. Jadiin gua CEO di gc lu
2. Buka obrolan suara / VCG lu
3. Typing `/userbotjoin` dan coba /play <nama lagu>
× Kalo Assistant Bot bergabung selamat menikmati musik, 
× Kalo Assistant Bot ga join Silahkan Tambahkan @{ASSISTANT_NAME} ke gc lu dan cobain lagi


**» Komen yg bisa dipake semua orang :**

 × /playlist : Untuk Menampilkan daftar putar Lagu sekarang
 × /current : Untuk Menunjukkan  Lagu sekarang yang sedang diputar
 × /song <judul lagu> : Untuk Mendownload lagu di YouTube 
 × /video <judul lagu> : Untuk Mendownload Video di YouTube dengan detail
 × /vsong <judul lagu> : Untuk Mendownload Video di YouTube dengan detail
 × /deezer <judul lagu> : Untuk Mendownload lagu dari deezer 
 × /saavn <judul lagu> : Untuk Mendownload lagu dari website saavn
 × /search <judul lagu> : Untuk Mencari Video di YouTube dengan detail

**» Admin doang yg bisa :**

× /play <judul lagu> : Untuk Memutar lagu yang Anda minta melalui youtube
× /play <link yt> : Untuk Memutar lagu yang Anda minta melalui link youtube
× /play <reply ke audio> : Untuk Memutar lagu yang Anda minta melalui file audio
× /dplay : Untuk Memutar lagu yang Anda minta melalui deezer
× /splay : Untuk Memutar lagu yang Anda minta melalui jio saavn
× /skip : Untuk Menskip pemutaran lagu ke Lagu berikutnya
× /pause : Untuk Menjeda pemutaran Lagu
× /resume : Untuk Melanjutkan pemutaran Lagu yang di pause
× /end : Untuk Memberhentikan pemutaran Lagu
× /userbotjoin - Untuk Mengundang asisten ke obrolan Anda
× /admincache - Untuk MemRefresh admin list
"""
      ]
