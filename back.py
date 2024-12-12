import sqlite3
import time

import json

import requests
import threading

import config
# import handlers
from aiogram import Bot
import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

bot = Bot(token=config.config.get('BOT_TOKEN'))


class Vpn:

    def __init__(self):
        self.panel_user = config.config.get("PANEL_USER")
        self.panel_pass = config.config.get("PANEL_PASS")
        self.session = requests.Session()
        self.headers = {"accept": "application/json"}
        self.base_url = config.BASE_URL
        if not self.headers.get("Authorization"):
            self.authorize()

        self.token_refresh_interval = 11 * 60 * 60  # 12 часов в секундах
        self.refresh_thread = threading.Thread(target=self._refresh_token)
        self.refresh_thread.daemon = True  # Обеспечиваем завершение потока при завершении основного потока

        self.refresh_thread.start()

    def _get(self, path: str) -> dict:
        url = f"{self.base_url}/{path}"
        try:
            response = self.session.request("GET", url, verify=False, headers=self.headers)
            response.raise_for_status()  # Проверка на успешный статус ответа
            if response.status_code == 200:
                return response.json()
            else:
                logging.error(f"Unexpected status code: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            logging.error(f"Failed to decode JSON response: {e}")
            return None

    def _post(self, path: str, data=None) -> dict:
        url = f"{self.base_url}/{path}"
        if not path == "api/admin/token":
            data = json.dumps(data)
        response = self.session.request("POST", url, verify=False, headers=self.headers, data=data)
        if response.status_code == 201 or response.status_code == 200:
            return response.json()

    def _put(self, path: str, data=None) -> dict:
        url = f"{self.base_url}/{path}"
        json_data = json.dumps(data)
        response = self.session.put(url, verify=False, headers=self.headers, data=json_data)

        if response.status_code == 200:
            # print(f"cmd xray PUT {path}, data: {data}")
            return response.json()
        else:
            print(f"cmd xray PUT not 200 status_code! {path}, data: {data}")

    def authorize(self) -> None:
        data = {
            "username": config.config.get('PANEL_USER'),
            "password": config.config.get('PANEL_PASS')
        }
        response = self._post("api/admin/token", data=data)
        token = response.get("access_token")
        self.headers["Authorization"] = f"Bearer {token}"

    def create_user(self, name: str) -> dict:
        data = {
            "username": name,
            "proxies": {
                "vless": {
                    "flow": "xtls-rprx-vision"
                }
            },
            "inbounds": {
                "vless": [
                    "VLESS TCP REALITY",
                    "VLESS TCP REALITY 2",
                    "VLESS TCP REALITY 3",
                    "VLESS TCP REALITY 4",
                    "VLESS TCP REALITY 5"
                ]
            },
            "data_limit": config.data_limit,
            "data_limit_reset_strategy": "month",
            "status": "active"
        }

        response = self._post("api/user", data=data)
        return response

    def plus_5(self, name: str) -> dict:

        data = {
            "username": name,
            "proxies": {
                "vless": {
                    "flow": "xtls-rprx-vision",
                },
            },
            "inbounds": {
                "vless": ["VLESS TCP REALITY", "VLESS TCP REALITY 2", "VLESS TCP REALITY 3", "VLESS TCP REALITY 4",
                          "VLESS TCP REALITY 5"],
            },

            "data_limit": 15 * 1024 * 1024 * 1024,
            "data_limit_reset_strategy": "day",
        }
        response = self._put(f"api/user/{name}", data=data)
        return response

    def edit_user_buy(self, name: str, day: int) -> dict:
        user = handlers.vpn.get_user(name)
        if user.get('status') == 'expired':
            x_time = time.time() + day * 86400
        if user.get('status') == 'active' and user.get('expire'):
            x_time = user['expire'] + day * 86400

        elif user.get('status'):
            x_time = time.time() + day * 86400

        data = {
            "expire": x_time,
            "data_limit": 30 * 1024 * 1024 * 1024,
            "data_limit_reset_strategy": "day",
        }
        response = self._put(f"api/user/{name}", data=data)
        return response

    def get_user(self, name: str) -> dict:
        response = self._get(f"api/user/{name}")
        return response

    def get_users(self):
        response = self._get(f'api/users/')
        return response

    def _refresh_token(self):

        while True:
            time.sleep(self.token_refresh_interval)  # Ждем 11 часов
            self.authorize()  # Повторная авторизация для получения нового токена

    def disable_user(self, name):
        data = {
            'status': 'disabled'
        }
        response = self._put(f"api/user/{name}", data=data)
        return response

    def enable_user(self, name):
        data = {
            'status': 'active'
        }
        return self._put(f"api/user/{name}", data=data)


v = Vpn()


class Db:

    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        chat_id TEXT NOT NULL,
        active INT NOT NULL,
        exp_time REAL,
        data_limit REAL NOT NULL
        )
        ''')

    def create_user(self, username, chat_id, active, data_limit, exp_time=None):
        with self.connection:
            # Добавляем нового пользователя
            res = self.cursor.execute(
                'INSERT INTO users (username, chat_id, active, exp_time, data_limit) VALUES (?, ?, ?, ?, ?)',
                (username, chat_id, active, exp_time, data_limit))

            return res

    def update_user_exp(self, username, exp_time):
        with self.connection:
            return self.cursor.execute("UPDATE users SET exp_time = ? WHERE username = ?", (exp_time, username,))

    def check_user(self, chat_id):
        with self.connection:
            return bool(self.cursor.execute('SELECT * FROM users WHERE username = ?', (chat_id,)).fetchmany(1))

    def get_users(self):
        with self.connection:
            return self.cursor.execute('SELECT * FROM users ').fetchall()

    def set_active(self, chat_id, active):
        with self.connection:
            return self.cursor.execute("UPDATE 'users' SET 'active' = ? WHERE 'chat_id' = ?", (active, chat_id,))

    def paid(self, chat_id):
        with self.connection:
            return self.cursor.execute('SELECT * FROM users WHERE username = ?', (chat_id,)).fetchmany(1)

    def transfer_exp_time(self, u_name, exp_time):
        with self.connection:
            return self.cursor.execute("UPDATE users SET exp_time = ? WHERE username = ?", (u_name, exp_time,))

    def get_username_by_id(self, chat_id):
        with self.connection:
            return self.cursor.execute('SELECT * FROM users WHERE chat_id = ?', (chat_id,)).fetchone()[1]

    def set_exp(self, chat_id, exp_time):
        with self.connection:
            return self.cursor.execute('UPDATE users SET exp_time = ? WHERE username= ?', (exp_time, chat_id,))

    def check_exp(self, chat_id):
        with self.connection:
            return self.cursor.execute('SELECT exp_time FROM users WHERE username = ?', (chat_id,)).fetchone()

    def get_user_by_id(self, chat_id):
        with self.connection:
            return self.cursor.execute('SELECT * FROM users WHERE chat_id = ?', (chat_id,)).fetchone()


d = Db('users.db')


def db_cr():
    all_users = v.get_users()
    for user in (all_users.get('users')):
        u_name = user.get('username')
        u_exp = user.get('expire')
        d.create_user(u_name, chat_id=0, total_paid=0, active=1)


def db_upd():
    all_users = v.get_users()
    for user in (all_users.get('users')):
        u_name = user.get('username')
        u_exp = user.get('expire')
        d.update_user_exp(u_name, u_exp)

