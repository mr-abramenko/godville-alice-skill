import json
import requests
import time
import random
import re
from bs4 import BeautifulSoup

def generate_response(version, session, user_data, session_data, app_data, text, tts, buttons, end_session):
    return {
        'version': version,
        'session': session,
        'user_state_update': {
            "data": user_data
        },
        "session_state": {
            "data": session_data
        },
        "application_state": {
            "data": app_data
        },
        'response': {
            # Respond with the original request or welcome the user if this is the beginning of the dialog and the request has not yet been made.
            'text': text,
            # https://yandex.ru/dev/dialogs/alice/doc/sounds.html
            "tts": tts,
            "buttons": buttons,
            # Don't finish the session after this response.
            'end_session': end_session
        }
    }

def clear_text(s):
    s = re.sub(r'\t', ' ', s)
    s = re.sub(r'\n', ' ', s)
    s = re.sub(r'\xa0', ' ', s)
    s = " ".join(s.split())
    return s

def handler(event, context):
    """
    Entry-point for Serverless Function.
    :param event: request payload.
    :param context: information about current execution context.
    :return: response to be serialized as JSON.
    """
# audio
    bell_tts = '<speaker audio="alice-sounds-things-bell-1.opus">'
    game_loss_tts = '<speaker audio="alice-sounds-game-loss-3.opus">'
    game_win_tts = '<speaker audio="alice-sounds-game-win-1.opus">'
    game_boot_tts = '<speaker audio="alice-sounds-game-boot-1.opus">'
    gong_tts = '<speaker audio="alice-music-gong-1.opus">'
    harp_tts = '<speaker audio="alice-music-harp-1.opus">'
    drums_tts = '<speaker audio="alice-music-drums-1.opus">'
    bagpipes_tts = '<speaker audio="alice-music-bagpipes-1.opus">'
    horn_tts = '<speaker audio="alice-music-horn-2.opus">'
    ship_tts = '<speaker audio="alice-sounds-transport-ship-horn-1.opus">'
    boss_tts = '<speaker audio="alice-sounds-human-walking-dead-3.opus">'
    arena_tts = '<speaker audio="alice-sounds-human-crowd-5.opus">'
    sword_tts = '<speaker audio="alice-sounds-things-sword-1.opus">'
    pause_tts = 'sil <[1000]>'

# чтение запроса пользователя
    if event.get('request').get('original_utterance'):
        utterance = event['request']['original_utterance']
    else:
        utterance = ""

# восстановление сохраненных данных
    if event.get('state').get('user').get('data'):
        user_data = event['state']['user']['data']
    else:
        user_data = dict()

    if event.get('state').get('session').get('data'):
        session_data = event['state']['session']['data']
    else:
        session_data = dict()

    if event.get('state').get('application').get('data'):
        app_data = event['state']['application']['data']
    else:
        app_data = user_data

# помощь
    try:
        if 'помощь' in utterance.lower() or 'что ты умеешь' in utterance.lower():
            text = f"Годвилль - игра слов и смыслов. \
Навык, позволяет читать записи из дневника Вашего героя в Годвилле, \
а так же следить за его состоянием, или узнать новости из газеты Годвилля. \
Чтобы начать, установите имя вашего бога. Для этого скажите фразу: 'установи имя бога'. \
После установки имени ваш герой будет вам отвечать. \
\n\n Герой иногда прислушивается к божественным словам. \
Так как все герои по своей природе тупае, то понять волю Всевышнего они \
могут только в том случае, если глас содержит знакомые ключевые слова (а также их корни). \
\n\n Навыком поддерживаются следующие ключевые слова: \n\n\
'установи имя бога', 'помощь', 'газета', 'молись', 'прана', 'задание', \
'характер', 'уровень', 'питомец', 'золото', 'аура', 'гильдия', \
'рюкзак', 'здоровье', 'дневник', 'арена', 'храм', 'пенсия', \
'ковчег', 'лаборатория', 'книга', 'души', 'лавка'. \
\n\n Если сказать фразу содержащую одино из них, то герой расскажет что-нибудь на эту тему."
            tts = " ".join([gong_tts,
                        text])
            buttons = [
                {
                    "title": "Что еще?",
                    "hide": True
                },
                {
                    "title": "Помощь",
                    "hide": True
                }
            ]
            return generate_response(event['version'], 
                                event['session'],
                                user_data,
                                session_data,
                                app_data,
                                text,
                                tts,
                                buttons,
                                end_session=False)

# установка имени бога
        if app_data.get('god_name'):
            if 'установи' in utterance.lower():
                user_data = dict()
                app_data = dict()
                text = "Хорошо. Теперь скажите имя бога, а \
лучше напишите, воспользовавшись навыком через телефон или компьютер. \
\n\n Если у вас нет бога и героя, то вы можете их зарегистрировать на сайте: https://godville.net. \
\n\n Для доступа к дневнику и большему набору данных о герое, можно установить имя бога как <имя_бога>/<ключ_api>. \
Ключ API можно получить в Вашем профиле по адресу https://godville.net/user/profile."
                tts = " ".join([text])
                buttons = []
                return generate_response(event['version'], 
                                event['session'],
                                user_data,
                                session_data,
                                app_data,
                                text,
                                tts,
                                buttons,
                                end_session=False)
        else:
            if utterance:
                app_data['god_name'] = utterance
                user_data['god_name'] = utterance
                text = f"Имя бога установлено! Да здравствует, {app_data['god_name']}! "
                tts = " ".join([gong_tts,
                            text])
                buttons = [
                    {
                        "title": "Что еще?",
                        "hide": True
                    },
                    {
                        "title": "Помощь",
                        "hide": True
                    }
                ]
                return generate_response(event['version'], 
                                event['session'],
                                user_data,
                                session_data,
                                app_data,
                                text,
                                tts,
                                buttons,
                                end_session=False)
            else:
                text = """Вам когда-нибудь хотелось почувствовать себя богом? \
Тогда вы по адресу. В этой игре каждый игрок становится божеством \
и обладателем персонального героя-почитателя, которым НЕ НУЖНО управлять \
— герой все cделает сам. Поначалу происходящее может показаться очень странным, \
но не спешите. Чтобы начать скажите имя своего божества. \
Для удобства воспользуйтесь навыком с телефона или компьютера. \
Если у вас еще нет божества, то зарегистрируйте его на сайте www.godville.net.
    """
                tts = " ".join([game_boot_tts,
                            text])
                buttons = [
                    {
                        "title": "Зарегистрировать бога",
                        "payload": {},
                        "url": "https://godville.net/login/register",
                        "hide": False
                    }
                ]
                return generate_response(event['version'], 
                                event['session'],
                                user_data,
                                session_data,
                                app_data,
                                text,
                                tts,
                                buttons,
                                end_session=False)
    except:
        text = "Что-то пошло не так. Попробуйте через минуту. \
Если ошибка повторяется, то установите заново имя вашего бога. \
Для этого скажите: 'Установи имя бога'. \
Для удобства воспользуйтесь навыком с телефона или компьютера. "
        tts = " ".join([game_boot_tts,
                        text,
                        game_loss_tts])
        buttons = [
                    {
                        "title": "Еще раз",
                        "hide": True
                    },
                    {
                        "title": "Установи имя бога",
                        "hide": True
                    },
                    {
                        "title": "Помощь",
                        "hide": True
                    }
        ]
        return generate_response(event['version'], 
                             event['session'],
                             user_data,
                             session_data,
                             app_data,
                             text,
                             tts,
                             buttons,
                             end_session=False)

# обновление данных героя
    try:
        hero_url = f"https://godville.net/gods/api/{app_data['god_name']}"
        
        if app_data.get('stamp'):
            if (time.time() - app_data['stamp'] > 60):
                app_data['stamp'] = time.time()
                app_data['gdv'] = json.loads(requests.get(hero_url).text)
        else:
            app_data['stamp'] = time.time()
            app_data['gdv'] = json.loads(requests.get(hero_url).text)
    except:
        text = "Что-то пошло не так. Попробуйте через минуту. \
Если ошибка повторяется, то установите заново имя вашего бога. \
Для этого скажите: 'Установи имя бога'. \
Для удобства воспользуйтесь навыком с телефона или компьютера. "
        tts = " ".join([game_boot_tts,
                        text,
                        game_loss_tts])
        buttons = [
                    {
                        "title": "Еще раз",
                        "hide": True
                    },
                    {
                        "title": "Установи имя бога",
                        "hide": True
                    },
                    {
                        "title": "Помощь",
                        "hide": True
                    }
                ]
        return generate_response(event['version'], 
                             event['session'],
                             user_data,
                             session_data,
                             app_data,
                             text,
                             tts,
                             buttons,
                             end_session=False)
    try:
# загрузка данных газеты        
        paper_url = "https://godville.net/news"
        paper_page = requests.get(paper_url)
        if not session_data.get('paper'):
            soup = BeautifulSoup(paper_page.content, "html.parser")

            session_data['paper'] = dict()
            session_data['paper']['date'] = soup.find('div', id="date").span.text + " день годвилльской эры"
            session_data['paper']['issue'] = soup.find('div', id="issue").text
            session_data['paper']['name'] = " ".join([soup.find('h1', id="name_1").text, soup.find('h1', id="name_2").text])
            session_data['paper']['headline_row'] = clear_text(soup.find('div', id="headline_row").text).replace("•", ".")
            session_data['paper']['astro'] = clear_text(soup.find_all('div', class_="fc clearfix")[0].text).replace("Астропрогноз", "Астропрогноз.")
            session_data['paper']['article'] = " - ".join([clear_text(soup.find_all('div', class_="article clearfix")[0].h3.text), clear_text(soup.find_all('div', class_="article clearfix")[0].p.text)])
            session_data['paper']['heroes_1'] = clear_text(soup.find_all('div', class_="hero clearfix")[0].text).replace("Их надо знать в лицо", "Их надо знать в лицо.")
            session_data['paper']['heroes_2'] = clear_text(soup.find_all('div', class_="hero clearfix")[1].text).replace("Идёт набор", "Идёт набор.")
            session_data['paper']['wanted'] = clear_text(soup.find_all('div', class_="game clearfix")[1].text).replace("Разыскиваются", "Разыскиваются.")
            session_data['paper']['buy_sell'] = clear_text(soup.find_all('div', class_="game clearfix")[2].text).replace("Куплю-продам", "Куплю-продам.")
            session_data['paper']['advertising'] = clear_text(soup.find_all('div', class_="add clearfix")[0].text).replace("Реклама", "Реклама.")
            session_data['paper']['idea_news'] = clear_text(soup.find_all('div', class_="news clearfix")[0].text).replace("Идейные новости", "Идейные новости.")
            session_data['paper']['news'] = clear_text(soup.find_all('div', class_="news clearfix")[1].text).replace("Как бы новости", "Как бы новости.")
            session_data['paper']['rate'] = clear_text(soup.find_all('div', class_="rate clearfix")[0].text).replace("Котировки", "Котировки...")
            session_data['paper']['footer'] = clear_text(soup.find('div', id="footer").text)
            session_data['paper']['mini_twits'] = clear_text(soup.find_all('div', class_="mini_twits")[0].p.text)
    except:
        session_data['paper'] = dict()
        session_data['paper']['news'] = "Встретившийся в кустах монстр умолял одолжить ему газету до завтра. \
Что поделаешь, не оставлять же его в беде. "
        session_data['paper']['idea_news'] = "Кажется газета потерялась. "

    try:
# генерация словаря фраз героя
        hero = dict()

        if session_data.get('paper'):
            hero['газет'] = list()
            hero['газет'].append(f"Судя по заголовку в газете сейчас {session_data['paper']['date']}. ")
            hero['газет'].append(f"Торговец продал мне газету: {session_data['paper']['name']} выпуск {session_data['paper']['issue']}. Почитаем... ")
            hero['газет'].append(f"{session_data['paper']['name']}: {session_data['paper']['headline_row']}")
            hero['газет'].append(f"{session_data['paper']['astro']}")
            hero['газет'].append(f"Так, что тут у нас в газете? {session_data['paper']['article']}")
            hero['газет'].append(f"Из газеты. {session_data['paper']['heroes_1']}")
            hero['газет'].append(f"Так так, что тут у нас. {session_data['paper']['heroes_2']}")
            hero['газет'].append(f"В газете пишут. {session_data['paper']['wanted']}")
            hero['газет'].append(f"А вот и мой любимый раздел. Так-так. {session_data['paper']['buy_sell']}")
            hero['газет'].append(f"Куда же без нее. {session_data['paper']['advertising']}")
            hero['газет'].append(f"{session_data['paper']['idea_news']}")
            hero['газет'].append(f"{session_data['paper']['news']}")
            hero['газет'].append(f"{session_data['paper']['rate']}")
            hero['газет'].append(f"На последнем листе газеты написано: {session_data['paper']['footer']}")
            hero['газет'].append(f"В газете пишут. {session_data['paper']['mini_twits']}")

    # молитва
        if app_data['gdv'].get('godname') and app_data['gdv']['name']:
            hero['моли'] = list()
            hero['моли'].append(f"Да здравствует, {app_data['gdv']['godname']}! \
Благослови меня, своего героя {app_data['gdv']['name']}! ")
            hero['моли'].append(f"{app_data['gdv']['name']} на связи! ")
            hero['моли'].append(f"Написал на столбе: здесь был {app_data['gdv']['name']}. ")
            hero['моли'].append(f"Приветствую, о {app_data['gdv']['godname']}. ")

    # пран
        if app_data['gdv'].get('godpower'): # api-key
            hero['пран'] = list()
            hero['пран'].append(f"Количество намоленой праны равно {app_data['gdv']['godpower']}! ")

    # задание
        if app_data['gdv'].get('quest'): # api-key
            hero['зада']= list()
            hero['зада'].append(f"Сейчас тружусь над тем, чтобы {app_data['gdv']['quest']}. ")
            if app_data['gdv'].get('quest_progress'): # api-key
                hero['зада'].append(f"Задание {app_data['gdv']['quest']} выполнено на {app_data['gdv']['quest_progress']}%! ")

    # характер
        if app_data['gdv'].get('alignment'):
            hero['характер'] = list()
            hero['характер'].append(f"Сегодня мой характер {app_data['gdv']['alignment']}. ")
            hero['характер'].append(f"Какой-то {app_data['gdv']['alignment']} я сегодня. ")

    # уровен
        if app_data['gdv'].get('level'):
            hero['уровен'] = list()
            hero['уровен'].append(f"Мой уровень мастерсва перевалил отметку {app_data['gdv']['level']}. ")
            if app_data['gdv'].get('exp_progress'): # api-key
                hero['уровен'].append(f"Уровень {app_data['gdv']['level']} прокачан на {app_data['gdv']['exp_progress']}%. ")
        
    # питомец
        if app_data['gdv'].get('pet'):
            hero['питом'] = list()
            if app_data['gdv'].get('pet').get('pet_level'):
                hero['питом'].append(f"Питомец мой, {app_data['gdv']['pet']['pet_class']} - \
{app_data['gdv']['pet']['pet_name']} имеет уровень \
{app_data['gdv']['pet']['pet_level']}. ")
                if app_data['gdv']['pet'].get('wounded'):
                    hero['питом'].append(f"{app_data['gdv']['pet']['pet_name']} \
получил контузию. Теперь бегаю, зарабатываю на лечение. ")
            else:
                hero['питом'].append(f" Эх, часто сожалею о том, что не получилось когда-то заработать \
достаточно золотых и вылечить от контузии {app_data['gdv']['pet']['pet_name']}. \
Но все равно он мой самый любимый {app_data['gdv']['pet']['pet_class']}. ")
        
    # золото
        if app_data['gdv']['gold_approx']: # api-key
            hero['золот'] = list()
            hero['золот'].append(f"В кармане у меня {app_data['gdv']['gold_approx']} золотых. ")
        
    # аура
        if app_data['gdv'].get('aura'): # api-key
            hero['аур'] = list()
            hero['аур'].append(f"Вокруг меня наблюдается присутствие ауры {app_data['gdv']['aura']}. ")
            hero['аур'].append(f"{app_data['gdv']['aura']}, {app_data['gdv']['aura']} и еще раз {app_data['gdv']['aura']}. ")
            hero['аур'].append(f"Аура {app_data['gdv']['aura']} положительно влияет на мою жизнь. ")

    # гильд
        if app_data['gdv'].get('clan'):
            hero['гильд'] = list()
            hero['гильд'].append(f"Моя гильдия {app_data['gdv']['clan']} лучше всех, \
именно потому что я являюсь ее членом! ")
            if app_data['gdv'].get('clan_position'):
                hero['гильд'].append(f"В гильдии я нашу гордое звание: \
{app_data['gdv']['clan_position']}! ")

    # рюкзак
        if app_data['gdv'].get('inventory_max_num'):
            hero['рюкзак'] = list()
            hero['рюкзак'].append(f"В мой рюкзак помещается {int(app_data['gdv']['inventory_max_num'])} предметов. ")
            if app_data['gdv'].get('inventory_num'): # api-key
                hero['рюкзак'].append(f"Мой рюкзак заполнен на \
{int(app_data['gdv']['inventory_num']/app_data['gdv']['inventory_max_num']*100)}%. ")
                hero['рюкзак'].append(f"В рюкзаке моем {int(app_data['gdv']['inventory_num'])} \
предметов из {app_data['gdv']['inventory_max_num']} возможных. ")
            if app_data['gdv'].get('activatables'): # api-key
                hero['рюкзак'].append(f"".join(["Из интересного в моем рюкзаке можно найти: ",
                                ", ".join(app_data['gdv']['activatables']), ". "]))
    # здоров
        if app_data['gdv'].get('max_health'):
            hero['здоров'] = list()
            hero['здоров'].append(f"Максимальный запас моего здоровья \
{int(app_data['gdv']['max_health'])} единиц. ")
            if app_data['gdv'].get('health'): # api-key
                hero['здоров'].append(f"Запас моего здоровья {int(app_data['gdv']['health'])} \
из {int(app_data['gdv']['max_health'])} возможных. ")

    # дневник
        hero['дневник'] = list()
        if app_data['gdv'].get('motto'):
            hero['дневник'].append(f"Мой девиз: {app_data['gdv']['motto']}. ")
            hero['дневник'].append(f"В любой непонятной ситуации я кричу: {app_data['gdv']['motto']}. ")
        if app_data['gdv'].get('motto'):
            hero['дневник'].append(f"Мой девиз: {app_data['gdv']['motto']}. ")
        if app_data['gdv'].get('distance'): # api-key
            hero['дневник'].append(f"О, столб. Ясно. До столицы еще {app_data['gdv']['distance']} столбов. ")
        if app_data['gdv'].get('diary_last'): # api-key
            hero['дневник'].append(f"{app_data['gdv']['diary_last']}. ")
        if app_data['gdv'].get('gender'):
            if app_data['gdv']['gender']=='male':
                hero['дневник'].append(f"Эх, хотелось мне жениться и чтобы \
много детишек ждали меня дома, каждый раз как с задания возвращаюсь. ")
            else:
                hero['дневник'].append(f"Эх, хотелось бы мне замуж. \
Тогда бы уже завязала с этими монстрами. Муж бы сражался, а я дома детей воспитывала. ")
        if app_data['gdv'].get('town_name'): # api-key
            hero['дневник'].append(f"Я в городе {app_data['gdv']['town_name']}. Куда бы пойти? ")
        if app_data['gdv'].get('expired'): # api-key
            if app_data['gdv'].get('godname'):
                hero['дневник'].append(f"{app_data['gdv']['godname']}, ты так давно \
не заходил в приложение или на сайт Годвилля, что я перестал обновлять дневник и данные о себе.\
Не вижу в этом смысла. ")
        if app_data['gdv'].get('godname'):
                hero['дневник'].append(f"Кажется я теряю с тобой связь {app_data['gdv']['godname']}. \
Зайди в приложение или на сайт Годвилля, сделай мне приятное, а то перестану обновлять дневник и данные. ")

    # арена
        if app_data['gdv'].get('arena_won') and app_data['gdv']['arena_lost']:
            hero['арен'] = list()
            hero['арен'].append(f"Все знают о моих успехах на арене. {app_data['gdv']['arena_won']} \
побед и {app_data['gdv']['arena_lost']} поражений. ")
        # Сделать это нужен api-key
        # arena_fight
        # fight_type
            # arena - арена (ЗПГ в том числе)
            # boss - босс (мини-квест)
            # boss_m - босс (зацеп)
            # challenge - тренировка
            # dungeon - подземелье
            # multi_monster - группа монстров
            # range - полигон
            # sail - морской поход

    # храм
        if app_data['gdv'].get('bricks_cnt'):
            hero['храм'] = list()
            hero['храм'].append(f"Для постройки храма мной собрано \
{app_data['gdv']['bricks_cnt']} золотых кирпичей из необходимых 1000. ")
            hero['храм'].append(f"План по строительству храма выполнен на {int(app_data['gdv']['bricks_cnt'])/10}%. ")
        if app_data['gdv'].get('temple_completed_at'):
            hero['храм'] = list()
            hero['храм'].append(f"На одном из кирпичей моего храма отпечатана дата и \
время его постройки: {app_data['gdv']['temple_completed_at']}. ")

    # пенси
        if app_data['gdv'].get('savings'):
            hero['пенси'] = list()
            hero['пенси'].append(f"На пенсию собрано \
{app_data['gdv']['savings']} золотых из необходимых 30 миллионов. ")
        if app_data['gdv'].get('savings_completed_at'):
            hero['пенси'] = list()
            hero['пенси'].append(f"Если меня разбудят и спросят в какой день я собрал на счастливую пенсию \
я отвечу: {app_data['gdv']['savings_completed_at']}. ")

    # ковчег
        if app_data['gdv'].get('wood_cnt'):
            hero['ковчег'] = list()
            hero['ковчег'].append(f"Мной собрано \
{app_data['gdv']['wood_cnt']} бревен из дерева гофер для ковчега из необходимых 1000. ")
            hero['ковчег'].append(f"Готовность ковчега равняется {int(app_data['gdv']['wood_cnt'])/10}%. ")
        if app_data['gdv'].get('ark_completed_at'):
            hero['ковчег'] = list()
            hero['ковчег'].append(f"Мной собрано \
{app_data['gdv']['wood_cnt']} гоферовых бревен, это больше чем нужно. \
Буду достраивать палубу ковчегу. ")
            hero['ковчег'].append(f"На одном из бревен моего ковчега выжжена дата и \
время его постройки: {app_data['gdv']['ark_completed_at']}. ")
            if app_data['gdv'].get('ark_f') and app_data['gdv'].get('ark_m'):
                if int(app_data['gdv'].get('ark_f'))!=1000:
                    hero['ковчег'].append(f"Ковчег мой заполнен тварями на \
{min(app_data['gdv']['ark_f'], app_data['gdv']['ark_m'])/10}%! \
Самцов в нем: {app_data['gdv']['ark_m']}, а самок: {app_data['gdv']['ark_f']} штук. ")
                    hero['ковчег'].append(f"{app_data['gdv']['ark_m']} и {app_data['gdv']['ark_f']} \
именно столько самцов и самок в моем ковчеге. ")

    # лаб
        if app_data['gdv'].get('boss_name'):
            hero['лаб'] = list()
            hero['лаб'].append(f"Имя собранного мной в лаборатории босса \
{app_data['gdv']['boss_name']}")

    # книг
        if app_data['gdv'].get('words'):
            hero['книг'] = list()
            hero['книг'].append(f"Число {int(app_data['gdv']['words'])} - именно \
столько слов, мной собранно из слогов для священной книги. ")
            hero['книг'].append(f"Священная книга написана на {int(app_data['gdv']['words'])/10}%. ")
        if app_data['gdv'].get('book_at'):
            hero['книг'] = list()
            hero['книг'].append(f"Дата окончания работы над священной книгой запомнится мне на всю жизнь: \
{app_data['gdv']['book_at']}. ")

    # душ
        if app_data['gdv'].get('souls_percent'):
            hero['душ'] = list()
            hero['душ'].append(f"{app_data['gdv']['souls_percent']} - именно столько душ найдено мной. ")

    # лавк
        if app_data['gdv'].get('shop_name'):
            hero['лавк'] = list()
            hero['лавк'].append(f"Горжусь своей лавкой под названием - {app_data['gdv']['shop_name']}. ")
            if app_data['gdv'].get('t_level'):
                hero['лавк'].append(f"Я торговец {app_data['gdv']['t_level']} уровня, между прочим. ")
            
    # генерация ответа
        text = ""
        if utterance:
            for key in hero.keys():
                if key in utterance.lower():
                    text += random.choice(hero[key])
        if app_data['gdv'].get('diary_last'):
                text = f"{app_data['gdv']['diary_last']}. "
        if not text:
            num_to_select = random.randint(1, 6)
            for key in random.sample(list(hero.keys()), num_to_select):
                text += random.choice(hero[key])
        
        tts = " ".join([bell_tts, text])
        buttons = [
            {
                "title": "Что еще?",
                "hide": True
            },
            {
                "title": "Помощь",
                "hide": True
            }
        ]
        
# удаление тяжёлых данных для сохранения
        if app_data['gdv'].get('diary_last'):
            del app_data['gdv']['diary_last']
        
        return generate_response(event['version'], 
                                event['session'],
                                user_data,
                                session_data,
                                app_data,
                                text,
                                tts,
                                buttons,
                                end_session=False)
    except:
        text = "Что-то пошло не так. Попробуйте через минуту. \
Если ошибка повторяется, то установите заново имя вашего бога. \
Для этого скажите: 'Установи имя бога'. \
Для удобства воспользуйтесь навыком с телефона или компьютера. "
        tts = " ".join([game_boot_tts,
                        text,
                        game_loss_tts])
        buttons = [
                    {
                        "title": "Еще раз",
                        "hide": True
                    },
                    {
                        "title": "Установи имя бога",
                        "hide": True
                    },
                    {
                        "title": "Помощь",
                        "hide": True
                    }
        ]
        return generate_response(event['version'], 
                             event['session'],
                             user_data,
                             session_data,
                             app_data,
                             text,
                             tts,
                             buttons,
                             end_session=False)
