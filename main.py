#!/usr/bin/env python3
from flask import Flask, render_template, Blueprint, request, flash, redirect, url_for

from manager_db import EventsDatabase, USERS_DB


__version__ = '0.1.0'


app = Flask(__name__)
app.secret_key = "we9jh89g8&GVE"

admin_bp = Blueprint('admin', __name__)


@app.route('/')
def index():
    return render_template('index.html')


@admin_bp.route('/admin')
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    events = EventsDatabase(USERS_DB)
    events.view_events()
    if request.method == 'POST':
        try:
            event_name = request.form['event_name']
            discipline = request.form['discipline']
            date = request.form['date']
            protocol_link = request.form['protocol_link']

            print("Received event data:")
            print("Event Name:", event_name)
            print("Discipline:", discipline)
            print("Date:", date)
            print("Protocol Link:", protocol_link)

            events_database = EventsDatabase(USERS_DB)
            events_database.add_event(event_name, discipline, date, protocol_link)

            flash('Данные сохранены!', 'flash-success')
        except Exception as e:
            flash('Ошибка сохранения в БД :(', 'flash-error')

        return redirect(url_for('admin'))

    return render_template('admin.html')


app.register_blueprint(admin_bp)


if __name__ == '__main__':
    app.run(debug=True)
