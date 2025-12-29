import logging
from asyncio.queues import QueueEmpty
from pyrogram import filters
from pytgcalls.exceptions import GroupCallNotFound
from pytgcalls.types.calls import Call

from ... import *
from ...modules.mongo.streams import *
from ...modules.utilities import queues

# ---------------- LOGGING ----------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("player-stop")


@app.on_message(cdx(["stp"]) & ~filters.private)
@sudo_users_only
async def stop_stream(client, message):
    chat_id = message.chat.id
    log.info(f"[STOP] Triggered | chat={chat_id}")

    try:
        a = await call.get_call(chat_id)
        log.info(f"[STOP] Call status={a.status}")

        if a.status in (Call.Status.PLAYING, Call.Status.PAUSED):
            try:
                queues.clear(chat_id)
                log.info("[STOP] Queue cleared")
            except QueueEmpty:
                log.info("[STOP] Queue already empty")

            await call.stop(chat_id)
            log.info("[STOP] Stream stopped")
            await eor(message, "**Stream Stopped!**")

        elif a.status == Call.Status.IDLE:
            log.info("[STOP] Nothing playing")
            await eor(message, "**Nothing Playing!**")

    except GroupCallNotFound:
        log.warning("[STOP] Bot not in VC")
        await eor(message, "**I am Not in VC!**")
    except Exception:
        log.exception("[STOP] Fatal error")


@app.on_message(cdz(["cstp"]))
@sudo_users_only
async def stop_stream_chat(client, message):
    user_id = message.from_user.id
    chat_id = await get_chat_id(user_id)
    log.info(f"[C-STOP] Triggered | user={user_id} | chat={chat_id}")

    if chat_id == 0:
        log.warning("[C-STOP] No stream chat set")
        return await eor(message, "**🥀 No Stream Chat Set❗**")

    try:
        a = await call.get_call(chat_id)
        log.info(f"[C-STOP] Call status={a.status}")

        if a.status in (Call.Status.PLAYING, Call.Status.PAUSED):
            try:
                queues.clear(chat_id)
                log.info("[C-STOP] Queue cleared")
            except QueueEmpty:
                log.info("[C-STOP] Queue already empty")

            await call.stop(chat_id)
            log.info("[C-STOP] Stream stopped")
            await eor(message, "**Stream Stopped!**")

        elif a.status == Call.Status.IDLE:
            log.info("[C-STOP] Nothing playing")
            await eor(message, "**Nothing Playing!**")

    except GroupCallNotFound:
        log.warning("[C-STOP] Bot not in VC")
        await eor(message, "**I am Not in VC!**")
    except Exception:
        log.exception("[C-STOP] Fatal error")


@app.on_message(cdz(["end"]) & ~filters.private)
@sudo_users_only
async def close_stream_(client, message):
    chat_id = message.chat.id
    log.info(f"[END] Triggered | chat={chat_id}")

    try:
        a = await call.get_call(chat_id)
        log.info(f"[END] Call status={a.status}")

        if a.status in (
            Call.Status.IDLE,
            Call.Status.PLAYING,
            Call.Status.PAUSED,
        ):
            try:
                queues.clear(chat_id)
                log.info("[END] Queue cleared")
            except QueueEmpty:
                log.info("[END] Queue already empty")

            await call.leave_group_call(chat_id)
            log.info("[END] Left VC")
            await eor(message, "**Stream Ended!**")

    except GroupCallNotFound:
        log.warning("[END] Bot not in VC")
        await eor(message, "**I am Not in VC!**")
    except Exception:
        log.exception("[END] Fatal error")


@app.on_message(cdz(["cend"]))
@sudo_users_only
async def close_stream_chat(client, message):
    user_id = message.from_user.id
    chat_id = await get_chat_id(user_id)
    log.info(f"[C-END] Triggered | user={user_id} | chat={chat_id}")

    if chat_id == 0:
        log.warning("[C-END] No stream chat set")
        return await eor(message, "**🥀 No Stream Chat Set❗**")

    try:
        a = await call.get_call(chat_id)
        log.info(f"[C-END] Call status={a.status}")

        if a.status in (
            Call.Status.IDLE,
            Call.Status.PLAYING,
            Call.Status.PAUSED,
        ):
            try:
                queues.clear(chat_id)
                log.info("[C-END] Queue cleared")
            except QueueEmpty:
                log.info("[C-END] Queue already empty")

            await call.leave_group_call(chat_id)
            log.info("[C-END] Left VC")
            await eor(message, "**Stream Ended!**")

    except GroupCallNotFound:
        log.warning("[C-END] Bot not in VC")
        await eor(message, "**I am Not in VC!**")
    except Exception:
        log.exception("[C-END] Fatal error")
