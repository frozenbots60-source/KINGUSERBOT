import logging
import aiohttp
from asyncio.queues import QueueEmpty
from pyrogram import filters
from pytgcalls.exceptions import *
from pytgcalls.types.calls import Call

from ... import *
from ...modules.mongo.streams import *
from ...modules.utilities import queues
from ...modules.utilities.streams import *

# ---------------- API ENDPOINTS ----------------

SEARCH_API = "https://search-api.kustbotsweb.workers.dev/search?q="
AUDIO_API = "https://divine-dream-fde5.lagendplayersyt.workers.dev/down?url="
VIDEO_API = "https://yt-api11-38da43a60341.herokuapp.com/vdown?url="

# ---------------- LOGGING ----------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("player")

# ---------------- INTERNAL SEARCH ----------------

async def api_search(query: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(SEARCH_API + query) as resp:
            if resp.status != 200:
                raise Exception(f"Search API failed: {resp.status}")
            data = await resp.json()
            return data["link"]

# ---------------- AUDIO PLAYER ----------------

@app.on_message(cdz(["ply", "play"]) & ~filters.private)
@sudo_users_only
async def audio_stream(client, message):
    chat_id = message.chat.id
    log.info(f"[AUDIO] Triggered | chat={chat_id}")

    aux = await eor(message, "**Processing ...**")

    try:
        calls = await call.calls
        chat_call = calls.get(chat_id)
        log.info(f"[AUDIO] chat_call={chat_call}")

        audio = (
            (message.reply_to_message.audio or message.reply_to_message.voice)
            if message.reply_to_message else None
        )

        type = "Audio"

        if audio:
            log.info("[AUDIO] Reply audio detected")
            await aux.edit("Downloading ...")
            file = await client.download_media(message.reply_to_message)
            log.info(f"[AUDIO] Downloaded file={file}")
        else:
            if len(message.command) < 2:
                log.warning("[AUDIO] No query provided")
                return await aux.edit(
                    "**🥀 ɢɪᴠᴇ ᴍᴇ sᴏᴍᴇ ǫᴜᴇʀʏ ᴛᴏ\nᴘʟᴀʏ ᴍᴜsɪᴄ ᴏʀ ᴠɪᴅᴇᴏ❗...**"
                )

            query = (
                message.text.split(None, 1)[1].split("?si=")[0]
                if "?si=" in message.text
                else message.text.split(None, 1)[1]
            )

            log.info(f"[AUDIO] Search query={query}")
            yt_url = await api_search(query)
            log.info(f"[AUDIO] Found URL={yt_url}")

            file = AUDIO_API + yt_url
            log.info(f"[AUDIO] Stream URL={file}")

        if chat_call:
            status = chat_call.status
            log.info(f"[AUDIO] Call status={status}")

            if status == Call.Status.IDLE:
                stream = await run_stream(file, type)
                log.info("[AUDIO] Stream created")
                await call.play(chat_id, stream)
                await aux.edit("Playing!")

            elif status in (Call.Status.PLAYING, Call.Status.PAUSED):
                position = await queues.put(chat_id, file=file, type=type)
                log.info(f"[AUDIO] Queued at {position}")
                await aux.edit(f"Queued At {position}")
        else:
            log.info("[AUDIO] No call object, trying to play")
            stream = await run_stream(file, type)
            log.info("[AUDIO] Stream created")

            try:
                await call.play(chat_id, stream)
                await aux.edit("Playing!")
            except NoActiveGroupCall:
                log.warning("[AUDIO] No active VC")
                return await aux.edit("No Active VC!")

    except Exception:
        log.exception("[AUDIO] Fatal error")
        await aux.edit("❌ Error while playing. Check logs.")

# ---------------- VIDEO PLAYER ----------------

@app.on_message(cdz(["vply", "vplay"]) & ~filters.private)
@sudo_users_only
async def video_stream(client, message):
    chat_id = message.chat.id
    log.info(f"[VIDEO] Triggered | chat={chat_id}")

    aux = await eor(message, "**Processing ...**")

    try:
        calls = await call.calls
        chat_call = calls.get(chat_id)

        video = (
            (message.reply_to_message.video or message.reply_to_message.document)
            if message.reply_to_message else None
        )

        type = "Video"

        if video:
            log.info("[VIDEO] Reply video detected")
            await aux.edit("Downloading ...")
            file = await client.download_media(message.reply_to_message)
        else:
            if len(message.command) < 2:
                return await aux.edit(
                    "**🥀 ɢɪᴠᴇ ᴍᴇ sᴏᴍᴇ ǫᴜᴇʀʏ ᴛᴏ\nᴘʟᴀʏ ᴍᴜsɪᴄ ᴏʀ ᴠɪᴅᴇᴏ❗...**"
                )

            query = (
                message.text.split(None, 1)[1].split("?si=")[0]
                if "?si=" in message.text
                else message.text.split(None, 1)[1]
            )

            log.info(f"[VIDEO] Search query={query}")
            yt_url = await api_search(query)
            log.info(f"[VIDEO] Found URL={yt_url}")

            file = VIDEO_API + yt_url
            log.info(f"[VIDEO] Stream URL={file}")

        if chat_call:
            status = chat_call.status

            if status == Call.Status.IDLE:
                stream = await run_stream(file, type)
                await call.play(chat_id, stream)
                await aux.edit("Playing!")

            elif status in (Call.Status.PLAYING, Call.Status.PAUSED):
                position = await queues.put(chat_id, file=file, type=type)
                await aux.edit(f"Queued At {position}")
        else:
            stream = await run_stream(file, type)
            try:
                await call.play(chat_id, stream)
                await aux.edit("Playing!")
            except NoActiveGroupCall:
                return await aux.edit("No Active VC!")

    except Exception:
        log.exception("[VIDEO] Fatal error")
        await aux.edit("❌ Error while playing. Check logs.")
