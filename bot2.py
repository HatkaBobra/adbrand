#!/usr/bin/env python3.8
from aiogram import types
from aiogram.types.web_app_info import WebAppInfo
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.types import Update
from aiogram.utils.media_group import MediaGroupBuilder
import sqlite3
import asyncio
import os
from typing import Any, Dict, BinaryIO, io
import datetime
import math
import random
import requests
from openai import AsyncOpenAI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.enums import ParseMode
import hashlib
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, PreCheckoutQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

connector = sqlite3.connect('taro.db', check_same_thread=False)
cursor = connector.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS extends(
   id INT PRIMARY KEY,
   username TEXT,
   fullname TEXT,
   join_date TIMESTAMP,
   paid INT,
   subs_dt TIMESTAMP)
""")

client = AsyncOpenAI(
    api_key="",  # This is the default and can be omitted
)

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
    print(chat_completion)
    print(chat_completion.choices[0].message.content);
    return chat_completion.choices[0].message.content

bot = Bot(token='')

async def main(app=None):
    dp = Dispatcher()
    router1 = Router()

    scheduler = AsyncIOScheduler(timezone='UTC')
    scheduler.start()

    class NatOrd(StatesGroup):
        gtinf = State()

    async def shedul_remprem():
        scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
        scheduler.add_job(shedul_repre, 'cron', hour='1')
        print('sheduled cours recalc')
        await bot.send_message(chat_id=adm_id, text='Sheduller remprem Once per 24 hours in 1 AM')

    async def shedul_repre():
        cursor.execute(f"""SELECT * from extends where subs_dt != null""")
        users = cursor.fetchall()
        print(users)
        for user in users:
            nndt = str(datetime.datetime.fromtimestamp(user[5]).date()).split('-')
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
                cursor.execute(f"UPDATE extends set subs_dt = '' where id = {user[0]}")
                connector.commit()
                cursor.execute(f"UPDATE extends set paid = 0 where id = {user[0]}")
                connector.commit()
                my_market = ''
                my_secret = ''
                my_prod = ''

                builder = InlineKeyboardBuilder()
                amns = ["990:Оплатить подпсику"]  # "11:тестовая",
                for am in amns:
                    shpid = user[0]
                    amount = am.split(':')[0]
                    rhash = f"{my_market}:{amount}:0:{my_secret}:Shp_id={shpid}:Shp_prd={my_prod}"
                    # print()
                    # print()
                    # print(rhash)
                    r = hashlib.md5(rhash.encode())

                    urlpth = f"&Shp_id={shpid}&Shp_prd={my_prod}"

                    builder.row(types.InlineKeyboardButton(
                        text=am.split(':')[1],
                        url=f'https://auth.robokassa.ru/Merchant/Index.aspx?MerchantLogin={my_market}&OutSum={amount}&InvoiceID={my_bill}&Description=Покупка услуг{urlpth}&SignatureValue={r.hexdigest()}')
                    )

                await bot.send_message(chat_id=user[0], text=f'Ваша подписка закончилась.\n\nПрислал кнопку для оплаты',
                                       reply_markup=builder.as_markup())
        cursor.execute(f"""SELECT * from extends where subs_dt != null""")
        nusers = cursor.fetchall()
        # print(nusers)
        await bot.send_message(chat_id=adm_id, text=f'{users} before\n{nusers} after remprem')

    async def shedul_remwish():
        nine_hours_from_now = datetime.datetime.now() + datetime.timedelta(minutes=30)
        print(datetime.datetime.now())
        scheduler = AsyncIOScheduler(timezone='UTC')
        scheduler.start()
        print('sheduled cours recalc')

    async def shedul_recalc(spd):
        cursor.execute(f"""SELECT * from extends where id = {spd}""")
        user = cursor.fetchone()

        if user[4] == 1:
            return
        else:
            print(1)
            # cursor.execute(f"UPDATE extends set paid = 0 where id = {spd}")
            # connector.commit()
        builder = InlineKeyboardBuilder()
        amns = ["990:Оплатить подпсику", "5000:Индивидуальный расклад"] #"11:тестовая",
        for am in amns:
            my_market = ''
            my_bill = ''
            prod = ''
            my_secret = ''
            shpid = spd
            amount = am.split(':')[0]
            rhash = f"{my_market}:{amount}:{my_bill}:{my_secret}:Shp_id={shpid}:Shp_prd={prod}"
            # print()
            # print()
            # print(rhash)
            r = hashlib.md5(rhash.encode())

            urlpth = f"&Shp_id={shpid}&Shp_prd={prod}"

            builder.row(types.InlineKeyboardButton(
                text=am.split(':')[1], url=f'https://auth.robokassa.ru/Merchant/Index.aspx?MerchantLogin={my_market}&OutSum={amount}&InvoiceID={my_bill}&Description=desc{urlpth}&SignatureValue={r.hexdigest()}')
            )

        await bot.send_message(chat_id=spd, text=f'Уже прошло 30 минут, вам осталось сделать 1 шаг и вы получите доступ к важной информации, которая повлияет на качество вашей жизни.', reply_markup=builder.as_markup())
        # print(users)

    kb_list = [
        [KeyboardButton(text="Подписаться на приватный канал")],
        # [KeyboardButton(text="Составить натальную карту")],
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True, one_time_keyboard=False)

    @dp.message(CommandStart())
    async def start(message: types.Message, state: FSMContext):
        now = datetime.datetime.now()
        local_now = now.astimezone()
        local_tz = local_now.tzinfo
        cursor.execute(f"""SELECT * from extends where id = {message.from_user.id}""")
        user = cursor.fetchone()

        if user == None:
            current_datetime = datetime.datetime.now()
            timestamp = current_datetime.timestamp()
            cursor.execute(u"""INSERT INTO extends(id, fullname, username, join_date, paid) VALUES (?, ?, ?, ?, ?)""",
                            (message.from_user.id, message.from_user.first_name, message.from_user.username, timestamp, 0))
            connector.commit()

        await message.answer('Добро пожаловать! Я создательница онлайн-платформы, посвященной женским темам саморазвития и самопознания.\n\nМой телеграм-канал — это пространство для женщин, стремящихся найти свое истинное предназначение, научиться саморефлексии и достигать целей в гармонии с собой.\n\nЯ приглашаю вас на путь глубокого понимания себя, внутренней гармонии и счастья. Здесь вы найдёте полезные практики, мотивирующие статьи и поддержку опытных специалистов, чтобы раскрыть свой потенциал и достичь успеха легко и уверенно.', reply_markup=keyboard)

    @router1.message((F.text.lower() == 'подписаться на приватный канал'))
    async def subscr(message: Message, state: FSMContext):
        builder = InlineKeyboardBuilder()
        amns = ["990:Оплатить подпсику", "5000:Индивидуальный расклад"] #"11:тестовая",
        for am in amns:
            my_market = ''
            my_bill = ''
            prod = ''
            my_secret = ''
            shpid = message.chat.id
            amount = am.split(':')[0]
            rhash = f"{my_market}:{amount}:{my_bill}:{my_secret}:Shp_id={shpid}:Shp_prd={prod}"
            r = hashlib.md5(rhash.encode())

            urlpth = f"&Shp_id={shpid}&Shp_prd={prod}"

            builder.row(types.InlineKeyboardButton(
                text=am.split(':')[1], url=f'https://auth.robokassa.ru/Merchant/Index.aspx?MerchantLogin={my_market}&OutSum={amount}&InvoiceID={my_bill}&Description=desc{urlpth}&SignatureValue={r.hexdigest()}')
            )

        nine_hours_from_now = datetime.datetime.now() + datetime.timedelta(minutes=30)

        scheduler.add_job(shedul_recalc, 'date', run_date=nine_hours_from_now, args=[message.from_user.id])
        await message.answer('Подписка на канал — всего 990 рублей.\n\nПрисоединяйтесь и начните преображаться уже сегодня!', reply_markup=builder.as_markup())

    @router1.message((F.text.lower() == 'составить натальную карту'))
    async def subscrd(message: Message, state: FSMContext):
        # await state.clear()
        kbb_list = [
            [KeyboardButton(text="Отмена")],
        ]
        kb = ReplyKeyboardMarkup(keyboard=kbb_list, resize_keyboard=True, one_time_keyboard=True)
        await message.answer('Доступно один раз или 3 раза в день по подписке\n\nВведи свои Дата, время и место рождения в виде:\n\n_03.05.1990 15:21, Астрахань_', parse_mode=ParseMode.MARKDOWN, reply_markup=kb)

        await state.set_state(NatOrd.gtinf)

    @router1.message(NatOrd.gtinf, (F.text.lower() != 'отмена'))
    async def parse_data(message: types.Message, state: FSMContext):
        answ = await askii(f'Составь натальную карту и максимально подробно опиши что она значит и что меня ждет, мои дата, время и место рождения: {message.text}')
        await message.answer(f'Немного подожди, я соединяюсь с Высшими силами\.\.',
                             parse_mode=ParseMode.MARKDOWN_V2)
        await message.answer(
            text=answ,
            parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)
        await state.clear()

    @router1.message(NatOrd.gtinf, (F.text.lower() == 'отмена'))
    async def reparse_data(message: types.Message, state: FSMContext):
        await message.answer(
            'Если понадоюблюсь - пиши',
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=keyboard)
        await state.clear()

    dp.include_router(router1)
    await shedul_remwish()
    await shedul_remprem()
    await dp.start_polling(app)

if __name__ == '__main__':
    asyncio.run(main(app=bot))