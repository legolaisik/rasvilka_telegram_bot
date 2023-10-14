import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import random

import sqlite3

conn = sqlite3.connect("bot.db")
cursor = conn.cursor()

from config import *
from sql_func import *
from api_func import *

logging.basicConfig(level=logging.INFO)

bot = Bot(token=bot_token, parse_mode=ParseMode.MARKDOWN_V2)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "start or restart bot")
    ])

class register(StatesGroup):
    hello = State()
    license = State()
    referal = State()

class lobby(StatesGroup):
    choose_action = State()

async def show_lk(user_id, conn: sqlite3.Connection):
    balance, total_win, total_game_wins, slot_coins, rating, count_players = await get_info(user_id, conn)
    rate = round(rating / count_players * 100)
    if rate == 0:
        rate = 1
    text = """🪪 *Информация о балансе*
🥇 *Вы в ТОП %d%% всех игроков*
🏆 *Сумма выигрыша:* %.2f TON
🪙 *Слот коинов:* %d

💵 *Баланс*: %.2f TON""" % (rate, total_win, slot_coins, balance,)
    text = text.replace('.', '\.')
    return text

lobby_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
lobby_keyboard.add(KeyboardButton('Информация о балансе 🪪'))
lobby_keyboard.add(KeyboardButton('Пополнить баланс 💎'))
lobby_keyboard.add(KeyboardButton('Играть 🎲'))
lobby_keyboard.add(KeyboardButton('Помощь 📃'))
lobby_keyboard.add(KeyboardButton('Вывод средств 💵'))

@dp.message_handler(state='*', commands=['start'])
async def start(message: types.Message, state: FSMContext):
    await register.hello.set()
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)

    if await check_user(message.from_user.id, conn):
        await lobby.choose_action.set()
        await bot.send_message(message.from_user.id, await show_lk(message.from_user.id, conn))
        await bot.send_message(message.from_user.id, "Привет 👋🏼\nВыбери действие 📝", reply_markup=lobby_keyboard)

    else:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        keyboard.add(KeyboardButton('Подтверждаю'))
        keyboard.add(KeyboardButton('Нет'))
        await register.license.set()

        await message.reply("Привет 👋🏼 \nПрежде, чем мы начнем играть, необходимо ознакомиться с нашим [_соглашением_ 📃](https://telegra.ph/Polzovatelskoe-soglashenie-01-13-5)", reply_markup=keyboard)

@dp.message_handler(state=register.license)
async def license_answer(message: types.Message, state: FSMContext):
    if message.text ==  'Подтверждаю':
        if await create_user(message.from_user.id, conn):
            await register.referal.set()
            async with state.proxy() as data:
                ref = data['hello']
            if ref == '':
                keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
                keyboard.add(KeyboardButton('У меня нет кода'))
                await bot.send_message(message.from_user.id, "Отлично 🙌 \nЕсли у вас есть реферальный код, введите его ниже 👇", reply_markup=keyboard)
            else:
                await set_referal(message.from_user.id, ref, conn)
                await bot.send_message(message.from_user.id, "Отлично 🙌")
                await lobby.choose_action.set()
                await bot.send_message(message.from_user.id, "Выбери действие 📝", reply_markup=lobby_keyboard)
        else:
            await bot.send_message(message.from_user.id, "Ошибка при регистрации")
    else:
        await message.reply("Чтобы продолжить необходимо принять [_соглашение_ 📃](https://telegra.ph/Polzovatelskoe-soglashenie-01-13-5)")
