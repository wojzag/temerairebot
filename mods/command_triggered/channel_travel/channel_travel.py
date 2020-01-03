import json
from telethon import TelegramClient
from telethon.tl.functions.messages import AddChatUserRequest
from telethon.tl.functions.channels import InviteToChannelRequest
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config.provider import TelegramConfig

class ChannelTravel():
    MODULE_PREFIX = "channel_travel::"

    def __init__(self, telegram_config: TelegramConfig):
        self.telegram_config = telegram_config
        self.channels = []
        with open('channels.json') as json_file:
            data = json.load(json_file)
            for c in data['channels']:
                self.channels.append(c)

        self.telegram_client = TelegramClient(self.telegram_config.telegram_api_session_name, self.telegram_config.telegram_api_id, self.telegram_config.telegram_api_hash).start()

    def command_channels(self, update, context):
        keyboard = []
        for c in self.channels:
            channel_name = c["name"]
            channel_id = c["id"]
            buttons = [
              InlineKeyboardButton(f"{channel_name}", callback_data="blep"),
              InlineKeyboardButton(f"+", callback_data=f"{self.MODULE_PREFIX}join_{channel_id}"),
              InlineKeyboardButton(f"-", callback_data=f"{self.MODULE_PREFIX}leave_{channel_id}")
            ]
            keyboard.append(buttons)

        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text("Panel kontrolny kanałów:", reply_markup=reply_markup)


    def callback_channels(self, update, context):
        query = update.callback_query

        if not query.data.startswith(self.MODULE_PREFIX):
          return

        _, query_data = query.data.split('::')
        instruction, chat_id = query_data.split("_")
        user_id = update.callback_query.from_user.id


        if instruction == 'join':
            self.telegram_client.loop.run_until_complete(self._invite_to_channel(chat_id, user_id))
        else:
            self.telegram_client.loop.run_until_complete(self._remove_from_channel(chat_id, user_id, context.bot))


    async def _invite_to_channel(self, chat_id, user_id):
        participants = await self.telegram_client.get_participants(int(chat_id))
        if user_id not in [o.id for o in participants]:
            group = await self.telegram_client.get_entity(int(chat_id))
            if group.__class__.__name__ == 'Channel':
                await self.telegram_client(InviteToChannelRequest(group, [user_id]))
            else:
                await self.telegram_client(AddChatUserRequest(group, user_id, fwd_limit=10))

    async def _remove_from_channel(self, chat_id, user_id, bot):
        participants = await self.telegram_client.get_participants(int(chat_id))
        if user_id in [o.id for o in participants]:
          bot.kick_chat_member(chat_id=int(chat_id), user_id=user_id)

