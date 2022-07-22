Akinator Telegram-Bot
=====================

@aki_efesx_bot

Бот реализует функционал Акинатора из известной [игры](https://akinator.com/)

Бекэнд развернут на облачных сервисах [Yandex.Cloud](https://cloud.yandex.ru/)

Задействованные облачные ресурсы:
---------------------------------
* [YandexCloudFunction](https://cloud.yandex.ru/services/functions)
* [YandexManagedServiceForYDB](https://cloud.yandex.ru/services/ydb)
* [YandexAPIGateway](https://cloud.yandex.ru/services/api-gateway)

Задействованные библиотеки:
---------------------------------
* [akinator.py](https://github.com/NinjaSnail1080/akinator.py)
* [pyTelegramBotAPI](https://pypi.org/project/pyTelegramBotAPI/)
* [ydb-python-sdk](https://github.com/ydb-platform/ydb-python-sdk)

Описание работы:
---------------------------------
Бот предлагает загадать персонажа, затем, задавая вопросы, пытается отгадать его.
Любое взаимодействие пользователя с ботом перенаправляется в Yandex Cloud Function с помощью Yandex API Gateway.
При начале игры, для каждого пользователя создается таблица в Yandex Database. Первичным ключом в таблице является id сообщения.
Объект класса AkinatorHelper, после отработки вызова функции (начало игры, ответ на вопрос), сохраняет свое состояние в таблицу соответсвующую id сообщения.
Перед отработкой функции (ответ на вопрос) объект класса AkinatorHelper загружает ранее сохраненное состояние из таблицы.


