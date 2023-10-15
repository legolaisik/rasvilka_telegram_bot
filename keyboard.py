from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard():
    main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    main_keyboard.add(KeyboardButton('Создать новый профиль'))
    main_keyboard.add(KeyboardButton('Удалить текущий профиль'))
    main_keyboard.add(KeyboardButton('Сменить профиль'))
    main_keyboard.add(KeyboardButton('Посмотреть вакансии по текущему профилю'))
    main_keyboard.add(KeyboardButton('Получить рекомендации по текущему профилю'))
    return main_keyboard

def get_skills_keyboard(skills: list):
    skills_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for skill in skills:
        skills_keyboard.add(KeyboardButton(skill))
    skills_keyboard.add(KeyboardButton('Дальше'))
    return skills_keyboard

def get_next_keyboard():
    next_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    next_keyboard.add(KeyboardButton('Дальше'))
    return next_keyboard

def get_employment_keyboard():
    employment_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    employment_keyboard.add(KeyboardButton('Полная занятость'))
    employment_keyboard.add(KeyboardButton('Частичная занятость'))
    employment_keyboard.add(KeyboardButton('Проектная работа'))
    employment_keyboard.add(KeyboardButton('Волонтерство'))
    employment_keyboard.add(KeyboardButton('Стажировка'))
    return employment_keyboard

def get_schedule_keyboard():
    schedule_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    schedule_keyboard.add(KeyboardButton('Полный день'))
    schedule_keyboard.add(KeyboardButton('Сменный график'))
    schedule_keyboard.add(KeyboardButton('Гибкий график'))
    schedule_keyboard.add(KeyboardButton('Удаленная работа'))
    schedule_keyboard.add(KeyboardButton('Вахтовый метод'))
    return schedule_keyboard

def get_education_keyboard():
    education_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    education_keyboard.add(KeyboardButton('Нет образования'))
    education_keyboard.add(KeyboardButton('Среднее профессиональное'))
    education_keyboard.add(KeyboardButton('Высшее'))
    return education_keyboard

def get_experience_keyboard():
    experience_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    experience_keyboard.add(KeyboardButton('Нет опыта'))
    experience_keyboard.add(KeyboardButton('От 1 года до 3 лет'))
    experience_keyboard.add(KeyboardButton('От 3 до 6 лет'))
    experience_keyboard.add(KeyboardButton('Более 6 лет'))
    return experience_keyboard