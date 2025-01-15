#!/usr/bin/env python3.8\
# -*- coding: utf-8 -*-
import time
import hashlib
from aiogram.types.web_app_info import WebAppInfo
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup
from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import Message, LabeledPrice
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, PreCheckoutQuery, InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import asyncio
import urllib
from aiogram.enums.content_type import ContentType
import os
import json
import datetime
from openai import AsyncOpenAI
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.methods.get_chat_member import GetChatMember
from apscheduler.schedulers.asyncio import AsyncIOScheduler

adm_id = 0

connector = sqlite3.connect('taro.db', check_same_thread=False)
cursor = connector.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS accounts(
   id INT PRIMARY KEY,
   username TEXT,
   fullname TEXT,
   phone TEXT,
   join_date TIMESTAMP,
   question_count INT,
   predic TEXT,
   asked INT,
   subscribe INT,
   predread INT,
   subs_dt TIMESTAMP,
   paidper INT)
""")

bot = Bot(token='')

client = AsyncOpenAI(
    api_key="",
)

tcoms = []

async def askii(tt) -> None:
    chat_completion = await client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": tt,
            }
        ],
        model="gpt-4o-mini",
    )
    print(chat_completion.choices[0].message.content)
    return chat_completion.choices[0].message.content


async def main(app=None):
    dp = Dispatcher()
    router1 = Router()

    kb_list = [
        [KeyboardButton(text="🔮✨  Задать вопрос  ✨🔮")],
        [KeyboardButton(text="Как работает бот"), KeyboardButton(text="Оформить подписку")], #KeyboardButton(text="Получить новые запросы")
        [KeyboardButton(text="Техподдержка"), KeyboardButton(text="Предсказание на день")],
        [KeyboardButton(text="Записаться на индивидуальный расклад")],
        [KeyboardButton(text="Получить 5 бесплатных запросов")],
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True, one_time_keyboard=False)

    async def shedul_remwish():
        scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
        scheduler.add_job(shedul_recalc, 'cron', hour='1')
        scheduler.start()
        print('sheduled cours recalc')
        await bot.send_message(chat_id=adm_id, text='Sheduller remwish Once per 24 hours in 1 AM')

    async def shedul_recalc():
        cursor.execute(f"""SELECT * from accounts where predic != ''""")
        users = cursor.fetchall()
        for user in users:
            cursor.execute(f"UPDATE accounts set predic = '' where id = {user[0]}")
            connector.commit()
            cursor.execute(f"UPDATE accounts set predread = 0 where id = {user[0]}")
            connector.commit()
        cursor.execute(f"""SELECT * from accounts where predic != ''""")
        nusers = cursor.fetchall()
        await bot.send_message(chat_id=adm_id, text=f'{users} before\n{nusers} after remwish')
        # print(users)

    async def shedul_remprem():
        scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
        scheduler.add_job(shedul_repre, 'cron', hour='1')
        scheduler.start()
        print('sheduled cours recalc')
        await bot.send_message(chat_id=adm_id, text='Sheduller remprem Once per 24 hours in 1 AM')

    async def shedul_repre():
        cursor.execute(f"""SELECT * from accounts where subs_dt != null""")
        users = cursor.fetchall()
        print(users)
        for user in users:
            nndt = str(datetime.datetime.fromtimestamp(user[10]).date()).split('-')
            crdt = str(datetime.datetime.fromtimestamp(datetime.datetime.today().timestamp()).date()).split('-')

            m = 0
            d = 0
            if nndt[1].startswith('0'):
                m = nndt[1][1:]
            else:
                m = nndt[1]
            if nndt[2].startswith('0'):
                d = nndt[2][1:]
            else:
                d = nndt[2]
            d1 = datetime.datetime(int(nndt[0]), int(m), int(d))
            if crdt[1].startswith('0'):
                m = crdt[1][1:]
            else:
                m = crdt[1]
            if crdt[2].startswith('0'):
                d = crdt[2][1:]
            else:
                d = crdt[2]
            d2 = datetime.datetime(int(crdt[0]), int(m), int(d))

            if (d1 > d2):

                cursor.execute(f"UPDATE accounts set subs_dt = '' where id = {user[0]}")
                connector.commit()
                cursor.execute(f"UPDATE accounts set paidper = 0 where id = {user[0]}")
                connector.commit()
                await bot.send_message(chat_id=user[0], text=f'Ваша подписка закончилась.\nДоступно запросов: {user[5]}')
        cursor.execute(f"""SELECT * from accounts where subs_dt != null""")
        nusers = cursor.fetchall()
        # print(nusers)
        await bot.send_message(chat_id=adm_id, text=f'{users} before\n{nusers} after remprem')



    @dp.message(CommandStart())
    async def start(message: types.Message, state: FSMContext):
        await message.answer('Погрузись в магический мир и узнай свой расклад 🙌\n\nЗадай свой вопрос и перечисли карты, которые ты выбрала, чтобы я исследовала твой путь.\n\nДля всех новых пользователей волшебства - 5 запросов абсолютно бесплатно!\n\nПримерный вопрос:\n"Что Рома чувствует ко мне?"\n\nПример расклада: 🎴\n3 Пентакли, Луна, 2 мечей. \n\nЕсли у тебя нет колоды ты сможешь выбрать карты онлайн.\n\nС любовью и магией, твой личный эзотерический гид - помощник от Ангелины. 💛\n\n\nP.S. Если что-то пошло не так, попробуйте написать /start\nКнопка меню находится снизу рядом с полем куда писать текст.\n\nТехподдержка @romaxms', reply_markup=keyboard)
        print(message)
        # # print(message.from_user.id)
        cursor.execute(f"""SELECT * from accounts where id = {message.from_user.id}""")
        user = cursor.fetchone()

        if user == None:
            current_datetime = datetime.datetime.now()
            timestamp = current_datetime.timestamp()
            cursor.execute(u"""INSERT INTO accounts(id, fullname, username, join_date, question_count, asked, subscribe, paidper) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                            (message.from_user.id, message.from_user.first_name, message.from_user.username, timestamp, 5, 0, 0, 0))
            connector.commit()

    class CrdOrd(StatesGroup):
        perque = State()
        peransw = State()
        perid =State()

    class PayOrd(StatesGroup):
        stars = State()


    kb_listd = [
        [KeyboardButton(text="🧿Мне нужны карты🧿", web_app=WebAppInfo(
            url='https://example.com/tarang'))],
        [KeyboardButton(text="Задать другой вопрос")],
        [KeyboardButton(text="Отмена")]
    ]
    kbd = ReplyKeyboardMarkup(keyboard=kb_listd, resize_keyboard=True, one_time_keyboard=True)

    @router1.message((F.text.lower() == '🔮✨  задать вопрос  ✨🔮'))
    async def start_conver(message: Message, state: FSMContext):
        print('\n\nhui\n\n')
        cursor.execute(f"""SELECT * from accounts where id = {message.from_user.id}""")
        user = cursor.fetchone()
        if user[5] == 0:
            await message.answer(
            'Чтобы получить новые запросы - нужно выбрать тариф и оплатить к нему доступ!\n\nОбрати внимание, что оплатить можно и с международных карт. Если ты хочешь оплатить иностранной картой нажми кнопку «международная оплата» \n\nВыбери тариф, который больше всего тебе откликается:\n\n\nЦены \n\n\n10 запросов - 111 руб.\n\n30 запросов -  333 руб.\n\n60 запросов - 555 руб.\n\n30 дней безлимита - 999 руб.\n\nМеждународная оплата ⭐️',
            parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)
            return

        if user[11] == 1:
            await message.answer(
            f'Ваша подписка актуальна до {datetime.datetime.fromtimestamp(user[10]).strftime("%Y-%m-%d")}\nЗапросов заморожено: {user[5]}.',
            parse_mode=ParseMode.MARKDOWN)
        else:
            await message.answer(
            f'У вас нет активной подписки.\nУ вас есть {user[5]} доступных запросов.',
            parse_mode=ParseMode.MARKDOWN)

        await message.answer("Введите ваш вопрос:")

        await state.set_state(CrdOrd.perque)

    @router1.message(CrdOrd.perque, ((F.text.lower() != 'техподдержка') & (F.text.lower() != 'как работает бот') & (F.text.lower() != 'записаться на индивидуальный расклад') & (F.text.lower() != 'получить 5 бесплатных запросов') & (F.text.lower() != 'оформить подписку') & (F.text.lower() != 'предсказание на день')))
    async def start_converd(message: Message, state: FSMContext):
        print('\n\nhui\n\n')
        if (message.text.lower() == 'отмена'):
            await state.clear()
            await message.answer("Если понадоблюсь - пиши", reply_markup=keyboard)
            return
        data = await state.update_data(perque=message.text)
        await message.answer(
            'Введи в поле для сообщения твои карты через запятую, если ты делаешь расклад на своей колоде\.\n\nЕсли у тебя нет своих карт, то жми кнопку 🧿Мне нужны карты🧿:',
            parse_mode=ParseMode.MARKDOWN_V2, reply_markup=kbd, one_time_keyboard=True)
        await state.set_state(CrdOrd.peransw)

    @dp.message(CrdOrd.peransw, (F.text.lower() == 'задать другой вопрос'))
    async def reparse_data(message: types.Message, state: FSMContext):
        await message.answer(
            '**Введи твой вопрос в поле для сообщения:**',
            parse_mode=ParseMode.MARKDOWN_V2)
        await state.set_state(CrdOrd.perque)


    @router1.message((F.text.lower() == 'как работает бот'))
    async def how_work(message: Message, state: FSMContext):
        await state.clear()
        await message.answer('Буду рад сделать расклад на любой вопрос, твой бот-таролог 💜\n\nКак мной пользоваться:\n\n1️⃣ Нажми на кнопку «Задать свой вопрос»\n\n2️⃣ Впиши свой вопрос в поле для сообщения и отправь его мне\n\n3️⃣ Если у тебя есть своя колода Таро:\n\n— Вытащи из неё 3 карты и отправь мне их названия (карты пиши через запятые)\n— Если у тебя выпала перевернутая карта, то так и пиши.\n\nПример написания карт:\nСолнце, паж кубков, перевернутая 7 пентаклей.\n\nЕсли у тебя нет своей колоды Таро:\n\n— Жми на кнопку «Мне нужны карты»\n— В открывшемся окне из 7 карт выбери 3 с помощью своей интуиции\n\n4️⃣ Жди 3-10 секунд и бот-таролог даст ответ на твой вопрос!\n\nТеперь ты знаешь, как мной пользоваться.\n\nЕсли спряталось меню, то его можно вызвать квадратной кнопкой в поле, где писать сообщение.\n\nС любовью, твой бот-таролог❤️\n\nСкорее жми кнопку «Задать свой вопрос» и я сделаю для тебя расклад.', reply_markup=keyboard)


    @router1.message((F.text.lower() == 'записаться на индивидуальный расклад'))
    async def subscr(message: Message, state: FSMContext):
        await state.clear()
        await message.answer('Если тебя сейчас что-то сильно беспокоит и ты не понимаешь, как самостоятельно решить этот вопрос, то записывайся на личный расклад.\n\nНапиши мне сюда @adm_id, чтобы найти выход из ситуации.', reply_markup=keyboard)


    @router1.message((F.text.lower() == 'техподдержка'))
    async def q_work(message: Message, state: FSMContext):
        await state.clear()
        await message.answer('Техподдержка \n\nЕсли у вас возникли проблемы с ботом, нажмите /start. \n\nЕсли бот так и не заработал в течение 10-15 минут, обратитесь в тех. поддержку @romaxms\n\nВнимание❗️ Перед тем, как задать вопрос нажмите на кнопку «Задать вопрос»', reply_markup=keyboard)

    @router1.pre_checkout_query()
    async def on_pre_checkout_query(
        pre_checkout_query: PreCheckoutQuery,
    ):
        await pre_checkout_query.answer(ok=True)

    @router1.message((F.text.lower() == 'получить 5 бесплатных запросов'))
    async def getgft(message: Message, state: FSMContext):
        await state.clear()
        l = await bot.get_chat_member(chat_id="@chat_id", user_id=message.from_user.id)
        cursor.execute(f"""SELECT * from accounts where id = {message.chat.id}""")
        user = cursor.fetchone()

        if l.status.lower() == "member" and user[8] == 0:
            newque = user[5] + 5

            cursor.execute(f"UPDATE accounts SET question_count = {newque} where id = {message.chat.id}")
            connector.commit()
            cursor.execute(f"UPDATE accounts SET subscribe = 1 where id = {message.chat.id}")
            connector.commit()
            await message.answer(
            f'Благодарю за подписку. Добавила 5 запросов\nЗапросов: {newque}',
            parse_mode=ParseMode.MARKDOWN)
            return

        await message.answer('За подписку на Telegram канал вы получаете пять бесплатных вопросов \n\n[«Я- Богиня»](https://t.me/link)\n\nАнгелина на канале вдохновляет женщин, делает расклады и рассказывает все о женской силе и энергии.\n\nПодпишись и забери свои пять бесплатных запросов \n\n(После подписки нажми снова на эту кнопку)', parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)

    @router1.message((F.text.lower() == 'оформить подписку'))
    async def getpay(message: Message, state: FSMContext):
        await state.clear()
        cursor.execute(f"""SELECT * from accounts where id = {message.chat.id}""")
        user = cursor.fetchone()
        builder = InlineKeyboardBuilder()
        my_market = ''
        my_bill = ''
        prod = ''
        my_secret = ''
        amns = ["111:10 запросов - 111 руб.", "333:30 запросов -  333 руб.", "555:60 запросов - 555 руб.", "999:30 дней безлимита - 999 руб."] #"11:тестовая",
        for am in amns:
            shpid = message.chat.id
            amount = am.split(':')[0]
            rhash = f"{my_market}:{amount}:{my_bill}:{my_secret}:Shp_id={shpid}:Shp_prd={prod}"
            r = hashlib.md5(rhash.encode())

            urlpth = f"&Shp_id={shpid}&Shp_prd={prod}"

            builder.row(types.InlineKeyboardButton(
                text=am.split(':')[1], url=f'https://auth.robokassa.ru/Merchant/Index.aspx?MerchantLogin={my_market}&OutSum={amount}&InvoiceID={my_bill}&Description=Desk{urlpth}&SignatureValue={r.hexdigest()}')
            )

        kbk = [
            [KeyboardButton(text="Международная оплата ⭐️")],
            [KeyboardButton(text="Отменить")]
        ]
        kebo = ReplyKeyboardMarkup(keyboard=kbk, resize_keyboard=True, one_time_keyboard=True)

        await message.answer('Оформить подписку\n\n\nЧтобы получить новые запросы - нужно выбрать тариф и оплатить к нему доступ!\n\nОбрати внимание, что оплатить можно и с международных карт. Если ты хочешь оплатить иностранной картой нажми кнопку «международная оплата»\n\nВыбери тариф, который больше всего тебе откликается:', parse_mode=ParseMode.MARKDOWN, reply_markup=builder.as_markup())
        await message.answer('Для Международной оплаты используй Stars - нажми кнопку снизу «Международная оплата ⭐️»', parse_mode=ParseMode.MARKDOWN, reply_markup=kebo)

    @router1.message((F.text.lower() == 'международная оплата ⭐️'))
    async def mppay(message: Message, state: FSMContext):
        kbkb = [
            [KeyboardButton(text="50 ⭐️")],
            [KeyboardButton(text="100 ⭐️")],
            [KeyboardButton(text="250 ⭐️")],
            [KeyboardButton(text="500 ⭐️")],
            [KeyboardButton(text="Отмена")]
        ]
        kebob = ReplyKeyboardMarkup(keyboard=kbkb, resize_keyboard=True, one_time_keyboard=True)
        await message.answer('10 запросов - 50 ⭐️\n\n30 запросов - 100 ⭐️\n\n60 запросов - 250 ⭐️\n\n30 дней безлимита - 500 ⭐️', parse_mode=ParseMode.MARKDOWN, reply_markup=kebob)
        await state.set_state(PayOrd.stars)

    @router1.message(PayOrd.stars, (F.text.lower() == "отмена"))
    async def cmpspay(message: Message, state: FSMContext):
        await state.clear()
        await message.answer("После оплаты вы получите доступ к предсказаниям и советам Таро, поможет в вашем развитии. Не упустите шанс увидеть ясный путь! 🌟", reply_markup=keyboard)

    @router1.message(PayOrd.stars, ((F.text.lower() == "50 ⭐️") | (F.text.lower() == "100 ⭐️") | (F.text.lower() == "250 ⭐️") | (F.text.lower() == "500 ⭐️")))
    async def mpspay(message: Message, state: FSMContext):
        await state.clear()
        amou = message.text.split(' ')[0]
        if message.text == "50 ⭐️":
            ggh = '10 запросов'
        if message.text == "100 ⭐️":
            ggh = '30 запросов'
        if message.text == "250 ⭐️":
            ggh = '60 запросов'
        if message.text == "500 ⭐️":
            ggh = 'подписки'
        br = InlineKeyboardBuilder()
        br.row(types.InlineKeyboardButton(
            text=f"Оплатить {amou} XTR", pay=True)
        )

        prices = [LabeledPrice(label="XTR", amount=amou)]
        await message.answer_invoice(
            title=f"ADtaroot",
            description=f"Приобритение {ggh}",
            prices=prices,
            provider_token="",
            payload=f"{amou}_stars",
            currency="XTR",
            reply_markup=br.as_markup()
        )
        await message.answer(f'Отправил кнопку для оплаты', reply_markup=keyboard)
        await state.clear()

    @router1.message(F.successful_payment)
    async def on_successful_paymentstrs(
        message: Message,
    ):
        buer = message.successful_payment.telegram_payment_charge_id
        amo = message.successful_payment.total_amount
        txtg = ""
        qqs = 0
        if amo == 50:
            txtg = "Благодарю, Вы приобрели 10 запросов"
            qqs = 10
        if amo == 100:
            txtg = "Благодарю, Вы приобрели 30 запросов"
            qqs = 30
        if amo == 250:
            txtg = "Благодарю, Вы приобрели 60 запросов"
            qqs = 60
        if amo == 500:
            txtg = "Благодарю, Вы приобрели подписку"

        cursor.execute(f"""SELECT * from accounts where id = {message.chat.id}""")
        user = cursor.fetchone()

        if amo != 4:
            cursor.execute(f"UPDATE accounts set question_count = {user[5] + qqs} where id = {message.from_user.id}")
            connector.commit()
        else:
            current_datetime = datetime.datetime.now() + datetime.timedelta(days=30)
            timestamp = current_datetime.timestamp()
            cursor.execute(f"UPDATE accounts set subs_dt = {timestamp} where id = {message.from_user.id}")
            connector.commit()
            cursor.execute(f"UPDATE accounts set paidper = 1 where id = {message.from_user.id}")
            connector.commit()

        await message.answer(
            f"{txtg}",
            message_effect_id="5104841245755180586",
        )

        await bot.send_message(chat_id=adm_id, text=f"{message.from_user.id} совершил оплату {amo} Stars",)

    @router1.message((F.text.lower() == 'предсказание на день'))
    async def wishr(message: Message, state: FSMContext):
        await state.clear()
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(
            text="Забери предсказание в приложении", web_app=WebAppInfo(
            url='https://example.com/wisher'))
        )

        cursor.execute(f"""SELECT * from accounts where id = {message.chat.id}""")
        user = cursor.fetchone()

        cursor.execute(f"""SELECT * from accounts where predic != ''""")
        users = cursor.fetchall()

        if user[6] == '' or user[6] == None:
            answ = await askii('сгенерируй случайное предсказание для печеньки с предсказанием длинной до 50 символов')
            answ = answ.replace('"', '')
            cursor.execute(f"UPDATE accounts SET predic = '{answ}' where id = {message.chat.id}")
            connector.commit()

        await message.answer('Предсказание , которое опишет твой предстоящий день.\n\n\nОна даст тебе подсказку, как прожить этот день лучше.✨\nЭто совершенно бесплатно и доступно для тебя каждый день🥰', parse_mode=ParseMode.MARKDOWN, reply_markup=builder.as_markup())

    @dp.message(CrdOrd.peransw, (F.content_type == ContentType.WEB_APP_DATA))
    async def parse_wadata(message: types.Message, state: FSMContext,):
        data = json.loads(message.web_app_data.data)
        dt = await state.update_data(peransw=message.text)
        cursor.execute(f"""SELECT * from accounts where id = {message.chat.id}""")
        user = cursor.fetchone()

        cursor.execute(f"UPDATE accounts SET asked = 1 where id = {message.chat.id}")
        connector.commit()
        que = f"{dt['perque']}\nМне выпали карты: {data['text']}"
        await message.answer(f'Тебе выпали карты: **{data["text"]}**',
                             parse_mode=ParseMode.MARKDOWN_V2)
        await message.answer(f'Немного подожди, я соединяюсь с Высшими силами\.\.',
                             parse_mode=ParseMode.MARKDOWN_V2)
        answ = await askii(que)
        await message.answer(answ,
                             parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)
        if user[11] == 1:
            await message.answer(
            f'Ваша подписка актуальна до {datetime.datetime.fromtimestamp(user[10]).strftime("%Y-%m-%d")}\nЗапросов заморожено: {user[5]}.',
            parse_mode=ParseMode.MARKDOWN)
        else:
            newque = user[5] - 1

            cursor.execute(f"UPDATE accounts SET question_count = {newque} where id = {message.chat.id}")
            connector.commit()
            await message.answer(
            f'У вас нет активной подписки.\nУ вас есть {newque} доступных запросов.',
            parse_mode=ParseMode.MARKDOWN)
        await state.clear()

    @dp.message(CrdOrd.peransw, ((F.content_type == ContentType.TEXT) & (F.text.lower() != 'задать другой вопрос')))
    async def parse_txtdata(message: types.Message, state: FSMContext):
        if (message.text.lower() == 'отмена'):
            await state.clear()
            await message.answer("Если захочешь задать вопрос жми кнопку 🔮✨  Задать вопрос  ✨🔮", reply_markup=keyboard)
            return

        dt = await state.update_data(peransw=message.text)
        que = f"{dt['perque']}\nМне выпали карты: {dt['peransw']}"

        cursor.execute(f"""SELECT * from accounts where id = {message.chat.id}""")
        user = cursor.fetchone()
        if user[11] == 1:
            print()
        else:
            newque = user[5] - 1
            cursor.execute(f"UPDATE accounts SET question_count = {newque} where id = {message.chat.id}")
            connector.commit()

        cursor.execute(f"UPDATE accounts SET asked = 1 where id = {message.chat.id}")
        connector.commit()
        await message.answer(f"Твои карты: **{dt['peransw']}**",
                             parse_mode=ParseMode.MARKDOWN_V2)
        await message.answer(f'Немного подожди, я соединяюсь с Высшими силами\.\.',
                             parse_mode=ParseMode.MARKDOWN_V2)
        answ = await askii(que)
        await message.answer(answ,
                             parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)
        await state.clear()
    #
    @router1.message(CrdOrd.perque, (F.text.lower() == 'отмена'))
    async def cancel_handler(message: Message, state: FSMContext) -> None:
        await state.clear()
        await message.answer("Если захочешь задать вопрос жми кнопку 🔮✨  Задать вопрос  ✨🔮", reply_markup=keyboard)

    @router1.message((F.text.lower() == 'отменить'))
    async def cncl_handler(message: Message, state: FSMContext) -> None:
        await state.clear()
        await message.answer("После оплаты вы получите доступ к предсказаниям и советам Таро, поможет в вашем развитии. Не упустите шанс увидеть ясный путь! 🌟", reply_markup=keyboard)

    @router1.message(CrdOrd.perque, (F.text.lower() == "отмена"))
    async def ccards(message: Message, state: FSMContext):
        await state.clear()
        await message.answer("Если понадоблюсь - пиши", reply_markup=keyboard)

    @dp.message(CrdOrd.peransw, (F.text.lower() == "отмена"))
    async def creadcards(message: Message, state: FSMContext):
        await state.clear()
        await message.answer("Если захочешь задать вопрос жми кнопку 🔮✨  Задать вопрос  ✨🔮", reply_markup=keyboard)

    dp.include_router(router1)
    await shedul_remwish()
    await shedul_remprem()
    await dp.start_polling(app)

if __name__ == '__main__':
    asyncio.run(main(app=bot))