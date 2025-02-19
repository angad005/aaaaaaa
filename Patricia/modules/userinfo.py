import html
from typing import List

from telegram import Update, ParseMode, MAX_MESSAGE_LENGTH
from telegram.ext.dispatcher import CallbackContext
from telegram.utils.helpers import escape_markdown

import Patricia.modules.sql.userinfo_sql as sql
from Patricia import dispatcher, SUDO_USERS, DEV_USERS
from Patricia.modules.helper_funcs.extraction import extract_user
from Patricia.modules.helper_funcs.decorators import kigcmd

@kigcmd(command='me', pass_args=True)
def about_me(update: Update, context: CallbackContext):
    args = context.args
    bot = context.bot
    message = update.effective_message
    user_id = extract_user(message, args)

    user = bot.get_chat(user_id) if user_id else message.from_user
    info = sql.get_user_me_info(user.id)

    if info:
        update.effective_message.reply_text(
            f"*{user.first_name}*:\n{escape_markdown(info)}",
            parse_mode=ParseMode.MARKDOWN,
        )
    elif message.reply_to_message:
        username = message.reply_to_message.from_user.first_name
        update.effective_message.reply_text(
            f"{username} hasn't set an info message about themselves yet!"
        )
    else:
        update.effective_message.reply_text(
            "You haven't set an info message about yourself yet!"
        )


@kigcmd(command='setme')
def set_about_me(update: Update, context: CallbackContext):
    bot = context.bot
    message = update.effective_message
    user_id = message.from_user.id
    if user_id in (777000, 1087968824):
        message.reply_text("Don't set info for Telegram bots!")
        return
    if message.reply_to_message:
        repl_message = message.reply_to_message
        repl_user_id = repl_message.from_user.id
        if repl_user_id == bot.id and (user_id in SUDO_USERS or user_id in DEV_USERS):
            user_id = repl_user_id

    text = message.text
    info = text.split(None, 1)

    if len(info) == 2:
        if len(info[1]) < MAX_MESSAGE_LENGTH // 4:
            sql.set_user_me_info(user_id, info[1])
            if user_id == bot.id:
                message.reply_text("Updated my info!")
            else:
                message.reply_text("Updated your info!")
        else:
            message.reply_text(
                "The info needs to be under {} characters! You have {}.".format(
                    MAX_MESSAGE_LENGTH // 4, len(info[1])
                )
            )

@kigcmd(command='bio', pass_args=True)
def about_bio(update: Update, context: CallbackContext):
    args = context.args
    bot = context.bot
    message = update.effective_message

    user_id = extract_user(message, args)
    user = bot.get_chat(user_id) if user_id else message.from_user
    info = sql.get_user_bio(user.id)

    if info:
        update.effective_message.reply_text(
            "*{}*:\n{}".format(user.first_name, escape_markdown(info)),
            parse_mode=ParseMode.MARKDOWN,
        )
    elif message.reply_to_message:
        username = user.first_name
        update.effective_message.reply_text(
            f"{username} hasn't had a message set about themselves yet!"
        )
    else:
        update.effective_message.reply_text(
            "You haven't had a bio set about yourself yet!"
        )
    message = update.effective_message
    if message.reply_to_message:
        repl_message = message.reply_to_message
        user_id = repl_message.from_user.id

        if user_id == message.from_user.id:
            message.reply_text(
                "Ha, you can't set your own bio! You're at the mercy of others here..."
            )
            return

        sender_id = update.effective_user.id

        if (
            user_id == bot.id
            and sender_id not in SUDO_USERS
            and sender_id not in DEV_USERS
        ):
            message.reply_text(
                "Erm... yeah, I only trust sudo users or developers to set my bio."
            )
            return

        text = message.text
        # use python's maxsplit to only remove the cmd, hence keeping newlines.
        bio = text.split(None, 1)

        if len(bio) == 2:
            if len(bio[1]) < MAX_MESSAGE_LENGTH // 4:
                sql.set_user_bio(user_id, bio[1])
                message.reply_text(
                    "Updated {}'s bio!".format(repl_message.from_user.first_name)
                )
            else:
                message.reply_text(
                    "A bio needs to be under {} characters! You tried to set {}.".format(
                        MAX_MESSAGE_LENGTH // 4, len(bio[1])
                    )
                )
    else:
        message.reply_text("Reply to someone's message to set their bio!")

@kigcmd(command='setbio')
def set_about_bio(update: Update, context: CallbackContext):
    message = update.effective_message
    sender_id = update.effective_user.id
    bot = context.bot

    if message.reply_to_message:
        repl_message = message.reply_to_message
        user_id = repl_message.from_user.id
        if user_id in (777000, 1087968824):
            message.reply_text("Don't set bio for Telegram bots!")
            return

        if user_id == message.from_user.id:
            message.reply_text(
                "Ha, you can't set your own bio! You're at the mercy of others here..."
            )
            return

        if user_id in [777000, 1087968824] and sender_id not in DEV_USERS:
            message.reply_text("You are not authorised")
            return

        if user_id == bot.id and sender_id not in DEV_USERS:
            message.reply_text("Erm... yeah, I only trust Eagle Union to set my bio.")
            return

        text = message.text
        bio = text.split(
            None, 1
        )  # use python's maxsplit to only remove the cmd, hence keeping newlines.

        if len(bio) == 2:
            if len(bio[1]) < MAX_MESSAGE_LENGTH // 4:
                sql.set_user_bio(user_id, bio[1])
                message.reply_text(
                    "Updated {}'s bio!".format(repl_message.from_user.first_name)
                )
            else:
                message.reply_text(
                    "Bio needs to be under {} characters! You tried to set {}.".format(
                        MAX_MESSAGE_LENGTH // 4, len(bio[1])
                    )
                )
    else:
        message.reply_text("Reply to someone to set their bio!")


def __user_info__(user_id):
    bio = html.escape(sql.get_user_bio(user_id) or "")
    me = html.escape(sql.get_user_me_info(user_id) or "")
    if bio and me:
        return f"\n<b>About user:</b>\n{me}\n<b>What others say:</b>\n{bio}\n"
    elif bio:
        return f"\n<b>What others say:</b>\n{bio}\n"
    elif me:
        return f"\n<b>About user:</b>\n{me}\n"
    else:
        return "\n"


from Patricia.modules.language import gs

def get_help(chat):
    return gs(chat, "userinfo_help")


__mod_name__ = "ʙɪᴏ•ᴀʙᴏᴜᴛ"
