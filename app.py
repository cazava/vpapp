from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)

# Функция для получения данных о пользователе по user_id
def query_user(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT chat_id FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check', methods=['POST'])
def check_user():
    user_id = request.json.get('user_id')
    user_name = query_user(user_id)
    if user_name:
        response = f"Пользователь найден: {user_name}"
    else:
        response = "Пользователь не найден."
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
