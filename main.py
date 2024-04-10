#!/usr/bin/env python3
from flask import Flask, render_template, Blueprint, request, flash, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_login import UserMixin

from manager_db import EventsDatabase, UserManager, USERS_DB
from competition_results import ManageResults

from time import sleep


__version__ = '0.2.1'


app = Flask(__name__)
app.secret_key = "we9jh89g8&GVE"

admin_bp = Blueprint('admin', __name__)

login_manager = LoginManager(app)

users = {'admin': {'password': 'admin_password'}}


# Класс пользователя
# Пример модели пользователя
class User(UserMixin):
    def __init__(self, user_id, username, password_hash, is_admin=False):
        self.id = user_id
        self.username = username
        self.password_hash = password_hash
        self.is_admin = is_admin

users = [
    User(1, 'admin', 'admin_password_hash', is_admin=True),
    User(2, 'user', 'user_password_hash')
]


@login_manager.user_loader
def load_user(user_id):
    for user in users:
        if user.id == user_id:
            return user
    return None


def is_admin(username, password):
    for user in users:
        if user.username == username and user.password_hash == password and user.is_admin:
            return True
    return False


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if is_admin(username, password):
            user = next((user for user in users if user.username == username), None)
            login_user(user)
            return redirect(url_for('admin'))
        else:
            flash('Неправильное имя пользователя или пароль', 'error')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы успешно вышли из системы', 'success')
    return redirect(url_for('login'))


@app.route('/')
@app.route('/index')
def index():
    events_database = EventsDatabase(USERS_DB)
    all_events = events_database.view_events()

    all_users = None
    try:
        users_manager = UserManager(USERS_DB)
        for event in all_events:
            all_users = users_manager.load_all_users(event[1])
    except Exception as e:
        print(e)
        pass

    # Логика обработки рангов
    print(all_events)
    return render_template('index.html', users=all_users, events=all_events)


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if not current_user.is_admin:
        flash('Недостаточно привилегий для доступа к этой странице', 'error')
        return redirect(url_for('/'))

    events_database = EventsDatabase(USERS_DB)
    all_events = events_database.view_events()

    try:
        users_manager = UserManager(USERS_DB)
        for event in all_events:
            print(event)
            all_users = users_manager.load_all_users(event[1])

    except Exception as e:
        flash(f'Ошибка чтения данных из БД :(\n\n{e}', 'flash-error')

    if request.method == 'POST':
        try:
            event_name = request.form['event_name']
            discipline = request.form['discipline']
            date = request.form['date']
            protocol_link = request.form['protocol_link']

            print("Отправленные данные:")

            events_database.add_event(event_name, discipline, date, protocol_link)
            print(event_name, discipline, date, protocol_link)

            flash('Данные сохранены!', 'flash-success')

            try:
                manage_results = ManageResults(protocol_link)
                manage_results.write_down_names_of_participants(event_name)
                flash('Результаты сохранены!', 'flash-success')
            except Exception as e:
                flash(f'Ошибка сохранения результатов :(\n\n{e}', 'flash-error')

        except Exception as e:
            print(e)
            flash(f'Ошибка сохранения в БД :(\n\n{e}', 'flash-error')

        return redirect(url_for('admin'))

    return render_template('admin.html')


app.register_blueprint(admin_bp)


if __name__ == '__main__':
    app.run(debug=True)
