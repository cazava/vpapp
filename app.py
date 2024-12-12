import asyncio
import datetime
import time

from flask import Flask, request, jsonify, render_template, send_from_directory
import sqlite3
from bot import bot, dp
from back import v, d

app = Flask(__name__)


def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])


user = 'PorokhovS'


# Функция для получения данных о пользователе по user_id
def query_user(username) -> dict:
    user_data = v.get_user(user)
    print(user_data)
    user_status = user_data.get('status')
    days = (user_data.get('expire') - time.time())
    days = round(days / 86400)
    exp = datetime.datetime.utcfromtimestamp(user_data['expire'])
    f_exp = exp.strftime('%d-%m-%Y')

    subscription_url = user_data.get('subscription_url')
    res = {
        'status': user_status,
        'days': days,
        'date': f_exp,
        'subscription_url': subscription_url

    }
    print(res)
    return res


@app.route('/')
def index():
    user_info = query_user(username=user)

    return render_template('app.html', date=user_info['date'], days=user_info['days'], status=user_info['status'])

# @app.route('/info')
# def check():
#     # limit_data = d.get_user_by_id(chat_id=user)
#     user_info = query_user(username=user)
#     return render_template('check.html', date=user_info['date'], days=user_info['days'], status=user_info['status'])


if __name__ == '__main__':
    app.run(port=5001, debug=True)
