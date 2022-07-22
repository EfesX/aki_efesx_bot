""" Logic for bot """
import os
from dotenv import load_dotenv
import telebot
from telebot.types import CallbackQuery
from akinatorhelper import AkinatorHelper
from keyboards import answer_keyboard
from keyboards import win_keyboard
from keyboards import begin_keyboard
from keyboards import menu_keyboard


load_dotenv(dotenv_path='secrets.env')
TELEGRAMM_TOKEN=os.getenv('TELEGRAMM_TOKEN')

bot = telebot.TeleBot(TELEGRAMM_TOKEN)
aki = AkinatorHelper()


@bot.callback_query_handler(func=lambda call: call.data == 'begin')
def begin_handler(call : CallbackQuery):
    """ Handler for start of the game """

    aki.start(str(call.message.chat.id), call.message.message_id, "ru", True)
    bot.edit_message_text(
        aki.question,
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=answer_keyboard()
    )

@bot.callback_query_handler(func=lambda call: call.data == 'win_yes')
def win_yes_handler(call: CallbackQuery):
    """ Game was ended. Bot guessed character. The Bot offers to start a new game """

    bot.edit_message_text(
        text = "Отлично! Я в себе не сомневался! Попробуем еще раз?",
        chat_id = call.message.chat.id,
        message_id = call.message.message_id,
        reply_markup = begin_keyboard()
    )

@bot.callback_query_handler(func=lambda call: call.data == 'win_no')
def win_no_handler(call: CallbackQuery):
    """ Game was ended. Bot not guessed character. The Bot offers to start a new game """

    bot.edit_message_text(
        text="Хмм... Требую реванш!!!",
        chat_id = call.message.chat.id,
        message_id = call.message.message_id,
        reply_markup = begin_keyboard()
    )

@bot.callback_query_handler(func=lambda call:
        ('y' in call.data) or
        ('n' in call.data) or
        ('idk' in call.data) or
        ('p' in call.data) or
        ('pn' in call.data)
)
def answer_handler(call: CallbackQuery):
    """ Handler for users's answers """

    try:
        aki.give_answer(call.message.chat.id, call.message.message_id, call.data)

        if aki.progression > 80:
            win = aki.win()
            person = win['name']
            img = win['absolute_picture_path']
            msg1 = "Ваш персонаж " + person + ".\n" + img
            msg2 = "Я угадал?"

            bot.send_message(call.message.chat.id, text = msg1)
            bot.send_message(call.message.chat.id, text = msg2, reply_markup=win_keyboard())
            bot.delete_message(call.message.chat.id, call.message.message_id)
        else:
            bot.edit_message_text(
                text=aki.question + "\n[" + str(aki.progression) + " %]",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                reply_markup=answer_keyboard()
            )

            bot.answer_callback_query(callback_query_id=call.id)
    except Exception:
        bot.delete_message(call.message.chat.id, call.message.message_id - 1)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(
            call.message.chat.id,
            text="Упс... Игровая сессия больше недоступна."
        )
        bot.send_message(
            call.message.chat.id,
            text="Хотите начать заново?",
            reply_markup=begin_keyboard()
        )

@bot.message_handler(commands=['start'])
def start_msg(message):
    """ Start of The Bot"""

    bot.send_message(
        message.chat.id,
        text = "Привет!",
        reply_markup=menu_keyboard()
    )
    bot.send_message(
        message.chat.id,
        text="Загадайте персонажа, а я попробую отгадать. Готовы?",
        reply_markup=begin_keyboard()
    )

@bot.message_handler(
    content_types =
        [ 'audio', 'photo', 'voice', 'video', 'document', 'location', 'contact', 'sticker']
)
def cleaner_handler(msg):
    """ Everething that does not relate to valid messages is deleted """
    bot.delete_message(msg.chat.id, msg.message_id)


@bot.message_handler(commands=['help'])
def help_msg(msg):
    """ Sends the help message """

    bot.send_message(
        msg.chat.id,
        "Всё просто! Вы загадываете персонажа. Бот пытается его угадать.",
        parse_mode='markdown'
    )

@bot.message_handler(content_types=['text'])
def text_handler(msg : telebot.types.Message):
    """ Handler for menu click """

    if msg.text == "Новая игра":
        start_msg(msg)
    elif msg.text == "О боте":
        bot.send_message(
            msg.chat.id,
            text = "Этот бот использует данные с сайта \
                    https://ru.akinator.com/\nРазработчик бота: @efesxzc"
        )
    elif msg.text == "Справка":
        help_msg(msg)
    else:
        bot.delete_message(msg.chat.id, msg.message_id)

if __name__ == "__main__":
    bot.delete_webhook()
    bot.infinity_polling()
