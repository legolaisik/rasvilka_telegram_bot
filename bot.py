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
from keyboard import *

logging.basicConfig(level=logging.INFO)

bot = Bot(token=bot_token, parse_mode=ParseMode.MARKDOWN_V2)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class register(StatesGroup):
    new_profile = State()
    enter_profile_name = State()
    enter_salary = State()
    enter_skills = State()
    enter_education = State()
    enter_experience = State()
    enter_jobtime = State()
    enter_jobtype = State()

class lobby(StatesGroup):
    hello = State()
    profiles_list = State()
    
class profile(StatesGroup):
    get_vacancies = State()
    vacancies_list = State()
    get_skills_recommendations = State()
    skills_recommendations_list = State()

async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "start or restart bot")
    ])
    
    
@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message, state: FSMContext):
    if not await db_check_user(message.from_user.id, conn):
        await db_create_user(message.from_user.id, conn)

        #Начинаем создавать профиль
        await bot.send_message(message.from_user.id, "Введите желаемую вакансию вида \'Junior Python Разработчик\'")
        await register.enter_profile_name.set()

    else:
        await bot.send_message(message.from_user.id, "Привет\! Выберите действие", reply_markup=main_keyboard)
        await lobby.profiles_list.set()


@dp.message_handler(state=register.enter_profile_name)
async def enter_profile_name_handler(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        data['enter_profile_name'] = message.text

    await bot.send_message(message.from_user.id, "Отлично! Должность %s введена" % message.text)
    await bot.send_message(message.from_user.id, "Введите желаемую зарплату. Если она не важна, нажмите дальше" % message.text, reply_markup = next_keyboard)

    await register.enter_salary.set()

@dp.message_handler(state=register.enter_salary)
async def enter_salary_handler(message: types.Message, state: FSMContext):

    if message.text == 'Дальше':

        async with state.proxy() as data:
            data['enter_salary'] = ''

        await bot.send_message(message.from_user.id, "Отлично\! Теперь вводите ваши ключевые навыки по одному. Например: Python, sql, Аналитика", reply_markup = next_keyboard)
        await register.enter_skills.set()

    else:

        try:
            salary = int(message.text)
            async with state.proxy() as data:
                data['enter_salary'] = str(salary)

            await bot.send_message(message.from_user.id, "Отлично\! Теперь вводите ваши ключевые навыки по одному. Например: Python, sql, Аналитика", reply_markup = next_keyboard)
            await register.enter_skills.set()
            
        except:
            await bot.send_message(message.from_user.id, "Введите число или нажмите Дальше", reply_markup = next_keyboard)
        

@dp.message_handler(state=lobby.profiles_list)
async def lobby_handler(message: types.Message, state: FSMContext):
    if message.text == 'Посмотреть вакансии по текущему профилю':
        answer = await get_vacancies(1, conn)
        await bot.send_message(message.from_user.id, answer, parse_mode=ParseMode.HTML)
    elif message.text == 'Получить рекомендации по текущему профилю':
        keys = await get_recomendations(1, conn)
        await bot.send_message(message.from_user.id, 'Вам бы подтянуть эти навыки: %s' % (', '.join(keys)), parse_mode=ParseMode.HTML)
    elif message.text == 'Создать новый профиль':

        #Начинаем создавать профиль
        await bot.send_message(message.from_user.id, "Введите желаемую вакансию вида \'Junior Python Разработчик\'")
        await register.enter_profile_name.set()
    

if __name__ == '__main__':

    executor.start_polling(dp, skip_updates=True)