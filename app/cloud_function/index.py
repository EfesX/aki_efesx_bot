""" Yandex Cloud Function for @aki_efesx_bot """

import telebot
from app import bot

def handler(event, context):
    """ Entrypoint for cloud function """
    #pylint: disable=unused-argument

    message = telebot.types.Update.de_json(event['body'])
    bot.process_new_updates([message])
    return {
        'statusCode': 200,
        'body': 'OK',
    }
