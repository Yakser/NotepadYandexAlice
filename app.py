import json
import logging
from random import choice
from flask_ngrok import run_with_ngrok
from flask import Flask, request

app = Flask(__name__)
run_with_ngrok(app)
logging.basicConfig(level=logging.INFO)

sessionStorage = {}

help_keywords = ['помощь', 'помоги', 'команды', 'help']
yes_keywords = ['да', 'конечно', 'ага', 'естественно']
no_keywords = ['нет', 'не-а', 'не']
misunderstanding_phrases = ['Я не понял, так да или нет?', 'Не понял. Да или нет?',
                            'Немного не понял. Напиши да или нет.']

notepad_ref = {
    "title": "Notepad",
    "url": "https://yakser-notepad.herokuapp.com",
    "hide": True
}
register_ref = {
    "title": "Регистрация",
    "url": "https://yakser-notepad.herokuapp.com/register",
    "hide": True
}
about_ref = {
    "title": "О приложении",
    "url": "https://yakser-notepad.herokuapp.com/about",
    "hide": True
}
settings_ref = {
    "title": "Регистрация",
    "url": "https://yakser-notepad.herokuapp.com/settings",
    "hide": True
}
manage_ref = {
    "title": "Регистрация",
    "url": "https://yakser-notepad.herokuapp.com/manage_folders",
    "hide": True
}
help_ = {
    'title': 'Помощь',
    'hide': True
}

illustrations = {
    'folders': '1030494/00ae0fcfe45a4367ce34',
    'register': '1030494/07036d1edd06cab66e3a',
    'settings': '997614/da65943d10727c046ced',
    'home': '1030494/926186e1262879746896',
    'about': '1652229/38cf2a87ec9bb9c345a0',
}

commands = {'.главная': {'text': 'Главная страница приложения со списком созданных папок', 'illustration': 'folders'},
            '.настройки': {
                'text': 'Настройки приложения - количество созданных папок и заметок,'
                        ' а также дата и время последнего изменения или редактирования',
                'illustration': 'settings'},
            '.справка': {'text': 'Notepad - удобная работа с заметками', 'illustration': 'about'}}
cmd_btns = {
    '.главная': {
        'title': '.главная',
        'hide': True
    },
    '.настройк': {
        'title': '.настройки',
        'hide': True
    },
    '.справка': {
        'title': '.справка',
        'hide': True
    }
}


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info('Response: %r', response)
    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']

    if any([word in req['request']['nlu']['tokens'] for word in help_keywords]):
        res['response']['text'] = ' Чтобы ознакомиться с частью возможностей' \
                                  ' приложения введи одну из команд:\n .главная - о главной странице\n' \
                                  ' .настройки - о настройках\n ' \
                                  ' .справка - о приложении в целом'

        res['response']['buttons'] = [
            *cmd_btns.values(), notepad_ref, help_
        ]
        return

    if any([word in req['request']['original_utterance'] for word in commands.keys()]):
        cmd = commands[req['request']['original_utterance']]
        res['response']['text'] = cmd['text']

        res['response']['card'] = {}
        res['response']['card']['type'] = 'BigImage'
        res['response']['card']['title'] = cmd['text']
        res['response']['card']['image_id'] = illustrations[cmd['illustration']]

        res['response']['buttons'] = [
            notepad_ref, help_
        ]
        return

    if req['session']['new']:
        sessionStorage[user_id] = {
            'use': None
        }

        res['response']['text'] = 'Привет! А ты пользуешься Notepad`ом?'
        res['response']['buttons'] = [
            {
                'title': 'Да',
                'hide': True
            },
            {
                'title': 'Нет',
                'hide': True
            },
            notepad_ref, help_
        ]
        return
    else:
        if sessionStorage[user_id]['use'] is None:

            if any([word in req['request']['nlu']['tokens'] for word in yes_keywords]):
                res['response']['text'] = 'Да ты крут! Если хочешь узнать побольше информации о приложении Notepad,' \
                                          ' то нажми кнопку Помощь'
                res['response']['buttons'] = [notepad_ref, help_]
                sessionStorage[user_id]['use'] = True
            elif any([word in req['request']['nlu']['tokens'] for word in no_keywords]):
                sessionStorage[user_id]['use'] = False
                res['response']['text'] = 'Так дело не пойдет, срочно регистрируйся по кнопке внизу!' \
                                          ' И создавай заметки, записывай свои мысли.'
                res['response']['buttons'] = [register_ref, notepad_ref, help_]

                res['response']['card'] = {}
                res['response']['card']['type'] = 'BigImage'
                res['response']['card']['title'] = 'Так дело не пойдет, срочно регистрируйся по кнопке внизу!'
                res['response']['card']['image_id'] = illustrations['register']
            else:
                res['response']['text'] = choice(misunderstanding_phrases)
                res['response']['buttons'] = [notepad_ref, help_]

        else:
            if req['request']['original_utterance'].lower().strip() == 'notepad':
                res['response']['text'] = 'Notepad - создавайте заметки, записывайте мысли, сохраняйте ссылки!' \
                                          'Приложение Notepad (от англ. “Блокнот, записная книжка”) позволяет' \
                                          ' создавать текстовые заметки с тегами и помещать их в различные папки.'
                res['response']['buttons'] = [about_ref, notepad_ref, help_]

                res['response']['card'] = {}
                res['response']['card']['type'] = 'BigImage'
                res['response']['card']['title'] = 'Главная страница приложения'
                res['response']['card']['image_id'] = illustrations['home']
            else:
                res['response'][
                    'text'] = 'Для получения более подробной информации рекомендуем перейти на сайт Notepad.'
                res['response']['buttons'] = [about_ref, notepad_ref, help_]


if __name__ == '__main__':
    app.run()
