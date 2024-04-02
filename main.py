#!/usr/bin/env python3
from flask import Flask, render_template, Blueprint, request, flash, redirect, url_for

from manager_db import EventsDatabase, UserManager, USERS_DB
from competition_results import ManageResults

from time import sleep


__version__ = '0.2.0'


app = Flask(__name__)
app.secret_key = "we9jh89g8&GVE"

admin_bp = Blueprint('admin', __name__)


@app.route('/')
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

    return render_template('index.html', users=all_users)


@admin_bp.route('/admin')
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    events_database = EventsDatabase(USERS_DB)
    all_events = events_database.view_events()

    try:
        users_manager = UserManager(USERS_DB)
        for event in all_events:
            print(event)
            all_users = users_manager.load_all_users(event[1])

    except Exception as e:
        # Если возникает ошибка при чтении из базы данных, обработаем ее здесь
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
