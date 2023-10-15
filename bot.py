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
    choose_from_profile = State()
    current_profile = State()
    
class profile(StatesGroup):
    get_vacancies = State()
    vacancies_list = State()
    get_skills_recommendations = State()
    skills_recommendations_list = State()

async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "start or restart bot")
    ])
    
    
@dp.message_handler(commands=['start'], state='*')
async def start_handler(message: types.Message, state: FSMContext):
    if not await db_check_user(message.from_user.id, conn):

        await db_create_user(message.from_user.id, conn)
        await bot.send_message(message.from_user.id, """Привет\!
Это бот Развилка, который поможет тебе понять и освоить траекторию твоей карьеры\:\)
Вводи данные ниже и освой навыки, которые понадобятся для работы мечты\!""")

        #Начинаем создавать профиль
        await bot.send_message(message.from_user.id, "Введите работу мечты\. Например: Технический директор\.")
        await register.enter_profile_name.set()

    else:
        await bot.send_message(message.from_user.id, "Привет\! Выберите действие", reply_markup=get_main_keyboard())
        await lobby.profiles_list.set()


@dp.message_handler(state=register.enter_profile_name)
async def enter_profile_name_handler(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        data['enter_profile_name'] = message.text

    await bot.send_message(message.from_user.id, "Отлично! Должность %s введена" % message.text, parse_mode=ParseMode.HTML)
    await bot.send_message(message.from_user.id, "Введите желаемую зарплату \(например, 50000\)\. Если она не важна, нажмите дальше", reply_markup = get_next_keyboard())

    await register.enter_salary.set()

@dp.message_handler(state=register.enter_salary)
async def enter_salary_handler(message: types.Message, state: FSMContext):

    if message.text == 'Дальше':

        await bot.send_message(message.from_user.id, "Отлично\! Теперь вводите ваши ключевые навыки по одному \(ввести один \-\> отправить\)\. Когда введены все, нажмите кнопку Дальше\. Например: Python, sql, Аналитика")
        await bot.send_message(message.from_user.id, 'Сейчас я Вам их подскажу\:\)')
        await bot.send_chat_action(message.from_user.id, 'typing')

        async with state.proxy() as data:
            data['enter_salary'] = ''
            skills = await get_skills(data['enter_profile_name'])
            data['wanted_skills'] = skills

        await bot.send_message(message.from_user.id, 'Выбирайте или вводите сами\. Потом нажмите дальше', reply_markup=get_skills_keyboard(skills))

        await register.enter_skills.set()

    else:

        try:
            salary = int(message.text)

            await bot.send_message(message.from_user.id, "Отлично\! Теперь вводите ваши ключевые навыки по одному \(ввести один \-\> отправить\)\. Когда введены все, нажмите кнопку Дальше\. Например: Python, sql, Аналитика")
            await bot.send_message(message.from_user.id, 'Сейчас я Вам их подскажу\:\)')
            await bot.send_chat_action(message.from_user.id, 'typing')
            
            async with state.proxy() as data:
                data['enter_salary'] = str(salary)
                skills = await get_skills(data['enter_profile_name'])
                data['wanted_skills'] = skills

            await bot.send_message(message.from_user.id, 'Выбирайте или вводите сами\. Потом нажмите дальше', reply_markup=get_skills_keyboard(skills))
            
            await register.enter_skills.set()

        except:
            await bot.send_message(message.from_user.id, "Ошибочка\.\.\.", reply_markup = get_next_keyboard())


@dp.message_handler(state=register.enter_skills)
async def enter_skills_handler(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        skills = data['wanted_skills']
        if 'enter_skills' in data:
            skills = list( set(skills) - set(data['enter_skills'].split(', ')) )

    if message.text == 'Дальше':

        async with state.proxy() as data:

            if 'enter_skills' not in data:

                await bot.send_message(message.from_user.id, "Вы еще не ввели ни одного навыка\:\( Уверены, что в Вас что\-то есть\)", reply_markup = get_skills_keyboard(skills))
           
            else:

                await bot.send_message(message.from_user.id, "Отлично\! Выберите уровень Вашего образования", reply_markup = get_education_keyboard())
                await register.enter_education.set()

    else:

        async with state.proxy() as data:

            if 'enter_skills' not in data:
                data['enter_skills'] = message.text
            else:
                data['enter_skills'] += ', %s' % message.text
                skills = list( set(skills) - set(data['enter_skills'].split(', ')) )

        await bot.send_message(message.from_user.id, "Записали %s, Еще?" % message.text, reply_markup = get_skills_keyboard(skills), parse_mode=ParseMode.HTML)


@dp.message_handler(state=register.enter_education)
async def enter_education_handler(message: types.Message, state: FSMContext):

    if message.text in ['Нет образования', 'Среднее профессиональное', 'Высшее']:

        async with state.proxy() as data:

            data['enter_education'] = message.text
        
        await bot.send_message(message.from_user.id, "Отлично\! Укажите Ваш опыт", reply_markup = get_experience_keyboard())
        await register.enter_experience.set()

    else:

        await bot.send_message(message.from_user.id, "Мы такого не знаем\(", reply_markup = get_education_keyboard())


@dp.message_handler(state=register.enter_experience)
async def enter_experience_handler(message: types.Message, state: FSMContext):

    if message.text in ['Нет опыта', 'От 1 года до 3 лет', 'От 3 до 6 лет', 'Более 6 лет']:

        async with state.proxy() as data:

            data['enter_experience'] = message.text
        
        await bot.send_message(message.from_user.id, "Отлично\! По какому графику хотите работать?", reply_markup = get_schedule_keyboard())
        await register.enter_jobtime.set()

    else:

        await bot.send_message(message.from_user.id, "Мы такого не знаем\(", reply_markup = get_experience_keyboard())


@dp.message_handler(state=register.enter_jobtime)
async def enter_jobtime_handler(message: types.Message, state: FSMContext):

    if message.text in ['Полный день', 'Сменный график', 'Гибкий график', 'Удаленная работа', 'Вахтовый метод']:

        async with state.proxy() as data:

            data['enter_jobtime'] = message.text
        
        await bot.send_message(message.from_user.id, "Отлично\! С каким типом занятости Вы хотите работать\?", reply_markup = get_employment_keyboard())
        await register.enter_jobtype.set()

    else:

        await bot.send_message(message.from_user.id, "Мы такого не знаем\(", reply_markup = get_schedule_keyboard())


@dp.message_handler(state=register.enter_jobtype)
async def enter_jobtype_handler(message: types.Message, state: FSMContext):

    if message.text in ['Полная занятость', 'Частичная занятость', 'Проектная работа', 'Волонтерство', 'Стажировка']:

        async with state.proxy() as data:

            data['enter_jobtype'] = message.text
            await db_create_profile(message.from_user.id, conn, data)

        await bot.send_message(message.from_user.id, "Отлично\! Профиль зарегистрирован", reply_markup = get_main_keyboard())
        await lobby.profiles_list.set()

    else:

        await bot.send_message(message.from_user.id, "Мы такого не знаем\(", reply_markup = get_employment_keyboard())


@dp.message_handler(state=lobby.choose_from_profile)
async def choose_from_profile_handler(message: types.Message, state: FSMContext):

    if message.text in await db_get_profiles(message.from_user.id, conn):

        await db_set_primary_profile(message.from_user.id, conn, message.text)
        await bot.send_message(message.from_user.id, "Отлично\! Профиль поменяли\)", reply_markup = get_main_keyboard())
        await lobby.profiles_list.set()

    else:

        profiles = await db_get_profiles(message.from_user.id, conn)
        profiles_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        for profile in profiles:
            profiles_keyboard.add(KeyboardButton(profile))
        await bot.send_message(message.from_user.id, "Мы такого не знаем\(", reply_markup = profiles_keyboard)
        

@dp.message_handler(state=lobby.profiles_list)
async def lobby_handler(message: types.Message, state: FSMContext):
    if message.text == 'Текущий профиль':
        profile_info = await db_get_cur_profile_info(message.from_user.id, conn)
        answer = "Должность: %s"%str(profile_info[0]) + "\n" + "Зарплата: %s"%str(profile_info[1]) + "\n" + "Навыки: %s"%str(profile_info[2]) \
            + "\n" + "Образование: %s"%str(profile_info[3]) + "\n" + "Опыт: %s"%str(profile_info[4]) + "\n" + "Занятость: %s"%str(profile_info[5]) \
                + "\n" + "Тип работы: %s"%str(profile_info[6])
        await bot.send_message(message.from_user.id, "Информация по текущему профилю\n" + answer, parse_mode=ParseMode.HTML)
    elif message.text == 'Посмотреть вакансии по текущему профилю':
        answer = await get_vacancies(message.from_user.id, conn)
        await bot.send_message(message.from_user.id, answer, parse_mode=ParseMode.HTML)
    elif message.text == 'Получить рекомендации по текущему профилю':

        await bot.send_message(message.from_user.id, 'Я уже начал собирать информацию...', parse_mode=ParseMode.HTML)
        await bot.send_chat_action(message.from_user.id, 'typing')
        
        keys,vacancy1, answer, vacancy2 = await get_recomendations(message.from_user.id, conn)
        
        if False not in [keys,vacancy1, answer, vacancy2]:

            await bot.send_message(message.from_user.id, 'Мы подготовили Вам развилку:)', parse_mode=ParseMode.HTML)

            message1 = """Основываясь на Ваших навыках, сейчас Вы можете посмотреть такую вакансию:
%s""" % vacancy1
            await bot.send_message(message.from_user.id, message1, parse_mode=ParseMode.HTML)

            message2 = """Вот наши советы как достичь работы мечты:
%s""" % answer
            await bot.send_message(message.from_user.id, message2, parse_mode=ParseMode.HTML)

            message3 = """Если вы подучите эти навыки: %s, то уже сможете метить и на такую вакансию:
%s""" % (', '.join(keys), vacancy2)
            await bot.send_message(message.from_user.id, message3, parse_mode=ParseMode.HTML)

        else:

            await bot.send_message(message.from_user.id, 'У нас произошла ошибка:(', parse_mode=ParseMode.HTML)
        
    elif message.text == 'Создать новый профиль':

        #Начинаем создавать профиль
        await bot.send_message(message.from_user.id, "Введите работу мечты\. Например\: Технический директор\.")
        await register.enter_profile_name.set()
    elif message.text == 'Сменить профиль':
        profiles = await db_get_profiles(message.from_user.id, conn)
        profiles_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
        for profile in profiles:
            profiles_keyboard.add(KeyboardButton(profile))
        await bot.send_message(message.from_user.id, "Выберите профиль:", reply_markup=profiles_keyboard)
        await lobby.choose_from_profile.set()
    elif message.text == 'Удалить текущий профиль':
        if len(await db_get_profiles(message.from_user.id, conn)) > 1:
            await db_delete_current_profile(message.from_user.id, conn)
            await bot.send_message(message.from_user.id, "Профиль удален\!", reply_markup=get_main_keyboard())
        else:
            await bot.send_message(message.from_user.id, "У Вас всего один профиль\( Сначала добавьте новый", reply_markup=get_main_keyboard())


if __name__ == '__main__':

    executor.start_polling(dp, skip_updates=True)