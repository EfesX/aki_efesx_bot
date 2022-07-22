"""Все клавиатуры и кнопки используемые ботом"""
import telebot

def answer_keyboard():
    """Клавиатура используется для ответа на вопрос Акинатора"""
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text='Да',            callback_data = 'y'))
    markup.add(telebot.types.InlineKeyboardButton(text='Нет',           callback_data = 'n'))
    markup.add(telebot.types.InlineKeyboardButton(text='Я не знаю',     callback_data = 'idk'))
    markup.add(telebot.types.InlineKeyboardButton(text='Скорее нет',    callback_data = 'pn'))
    markup.add(telebot.types.InlineKeyboardButton(text='Скорее да',     callback_data = 'p'))
    return markup

def win_keyboard():
    """Клавиатура используется при выдвижении предположения Акинатором"""
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            text='Да, именно так!',
            callback_data = 'win_yes'
        )
    )
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            text='Нет, это не так!.',
            callback_data = 'win_no'
        )
    )
    return keyboard

def begin_keyboard():
    """Клавиатура используется для начала игры"""
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            text='Начнём!',
            callback_data = 'begin'
        )
    )
    return keyboard



def menu_keyboard():
    """Меню"""
    keyboard = telebot.types.ReplyKeyboardMarkup(True)
    keyboard.row('Новая игра')
    keyboard.row('О боте')
    keyboard.row('Справка')
    return keyboard
