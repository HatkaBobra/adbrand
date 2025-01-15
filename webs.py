import sqlite3
import flask as flask
from flask import redirect
from flask import render_template
import requests
import datetime
import hashlib

app = flask.Flask(__name__)

cn = sqlite3.connect('taro.db', check_same_thread=False)
cr = cn.cursor()

adm_id = 0
token_bot = ''

@app.route('/')
def draw_main_page():
    return render_template('mn.html')

@app.route('/f88112h3')
def draw_offrt():
    return flask.send_file('oferta.docx', as_attachment=False)

@app.route('/tarang')
def draw_taro_page():
    return render_template('rand.html')

@app.route('/robokassa_callback/success')
def succ_pay():
    cost = flask.request.args['OutSum']
    number = flask.request.args['InvId']
    signature = flask.request.args['SignatureValue']
    spid = flask.request.args['Shp_id']
    adprod = flask.request.args['Shp_prd']

    my_market = ''
    my_secret = ''

    rhash = f"{my_market}:{int(cost.split('.')[0])}:{number}:{my_secret}:Shp_id={spid}:Shp_prd={adprod}"
    rb = hashlib.md5(rhash.encode()).hexdigest()
    if rb != signature:
        return "Bad sign"

    if adprod == "tarotad":
        cr.execute(f"""SELECT * from accounts where id = {spid}""")
        user = cr.fetchone()
        qqs = 0
        if cost == '111.00':
            qqs = 10
        if cost == '333.00':
            qqs = 30
        if cost == '555.00':
            qqs = 60
        if cost == '999.00':
            qqs = 100
        ttb = ""

        if qqs != 100:
            cr.execute(f"UPDATE accounts set question_count = {user[5] + qqs} where id = {spid}")
            cn.commit()
            ttb = f"Благодарю, Вы приобрели {qqs} запросов"
        else:
            current_datetime = datetime.datetime.now() + datetime.timedelta(days=30)
            timestamp = current_datetime.timestamp()
            cr.execute(f"UPDATE accounts set subs_dt = {timestamp} where id = {spid}")
            cn.commit()
            cr.execute(f"UPDATE accounts set paidper = 1 where id = {spid}")
            cn.commit()
            ttb = f'Благодарю, подписка оформлена до {datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")}'


        payload = {
            "chat_id": adm_id,
            "text": f"{spid} совершил оплату {cost}",
        }
        requests.post(url=f'https://api.telegram.org/bot{token_bot}/sendMessage', json=payload)

        payload = {
            "chat_id": adm_id,
            "text": f"{spid} совершил оплату {cost}",
        }
        r = requests.post(url=f'https://api.telegram.org/bot{token_bot}/sendMessage', json=payload)

        payload = {
            "chat_id": spid,
            "text": ttb,
        }
        r = requests.post(url=f'https://api.telegram.org/bot{token_bot}/sendMessage', json=payload)

        return redirect('https://t.me/TarotAD_bot')

    if adprod == "adtaroot":
        if cost == 990:
            cr.execute(f"""SELECT * from extends where id = {spid}""")
            user = cr.fetchone()

            payload = {
                "chat_id": adm_id,
                "text": f"{spid} совершил оплату {cost}",
            }
            r = requests.post(url=f'https://api.telegram.org/bot{token_bot}/sendMessage', json=payload)

            payload = {
                "chat_id": spid,
                "text": "Благодарю за приобритение подписки. Твоя ссылка в приватный канал:\n[«Подписаться на канал»](https://t.me/link)",
                "parse_mode": "Markdown"
            }
            r = requests.post(url=f'https://api.telegram.org/bot{token_bot}/sendMessage', json=payload)
            cr.execute(f"UPDATE extends set paid = 1 where id = {spid}")
            cn.commit()

        if cost == 5000:
            print(1)

        return redirect('https://t.me/ADtaroot_bot')



@app.route('/t/robokassa_callback/fail')
def fail_pay():
    print('fail pay')
    return "FAIL"

@app.route('/t/robokassa_callback/result')
def rez_pay():
    return f'OK{flask.request.args["InvId"]}'

@app.route('/wisher')
def draw_wish_page():
    return render_template('wisher.html')

@app.route('/getwish/<pid>')
def getwsh(pid):
    cr.execute(f"""SELECT * from accounts where id = {pid}""")
    user = cr.fetchone()
    return {"pwish":str(user[6]),
            "pread":str(user[9])}

@app.route('/readwish/<pid>')
def readwsh(pid):
    cr.execute(f"UPDATE accounts set predread = 1 where id = {pid}")
    cn.commit()
    cr.execute(f"""SELECT * from accounts where id = {pid}""")
    user = cr.fetchone()
    return {"pwish":str(user[6])}
