import logging
import telegram
from dotenv import load_dotenv
import os
from telegram.ext import Updater
from telegram.ext import CommandHandler, CallbackQueryHandler
from mods.command_triggered.channel_travel.channel_travel import ChannelTravel
from config.provider import TelegramConfig

def error(update, context):
  logger.warning('Update "%s" caused error "%s"', update, context.error)

load_dotenv()

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

telegram_config = TelegramConfig()

bot = telegram.Bot(token=telegram_config.bot_token)
updater = Updater(token=telegram_config.bot_token, use_context=True)

channel_travel = ChannelTravel(telegram_config)

updater.dispatcher.add_handler(CommandHandler('channels', channel_travel.command_channels))
updater.dispatcher.add_handler(CallbackQueryHandler(channel_travel.callback_channels))

updater.dispatcher.add_error_handler(error)

updater.start_polling()
updater.idle()
