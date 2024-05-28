# -*- coding: UTF-8 -*-

from flask import Flask, render_template, request, flash, redirect, url_for, session
# from manager_db import EventsDatabase, UserManager, USERS_DB, RangsManager, LoginManager
# from competition_results import ManageResults

import hashlib

from time import sleep


__version__ = '0.3.0'

application = Flask(__name__)
application.secret_key = "we9jh89g8&GVE"


@application.route("/")
@application.route("/index")
def index():
    rangs_database = RangsManager(USERS_DB)
    all_events = rangs_database.view_rangs()

    all_users = None
    try:
        users_manager = UserManager(USERS_DB)
        for event in all_events:
            all_users = users_manager.load_all_users(event[1])
    except Exception as e:
        print(e)
        pass

    # Логика обработки рангов
    return render_template('index.html', users=all_users, rangs=all_events)


@application.route('/admin')
def admin():
    
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    return render_template('admin.html')


@application.route('/admin/create_comp', methods=['GET', 'POST'])
def create_comp():
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    events_database = EventsDatabase(USERS_DB)
    if request.method == 'POST':
        try:
            event_name = request.form['event_name']
            discipline = request.form['discipline']
            date = request.form['date']
            protocol_link = request.form['protocol_link']

            print("Отправленные данные:")

            event_id = events_database.add_event(event_name, discipline, date, protocol_link)
            print(event_id, event_name, discipline, date, protocol_link)

            flash('Данные сохранены!', 'flash-success')

            try:
                manage_results = ManageResults(protocol_link)
                manage_results.write_down_names_of_participants(event_id)
                flash('Результаты сохранены!', 'flash-success')
            except Exception as e:
                print(e)
                flash(f'Ошибка сохранения результатов :(\n\n{e}', 'flash-error')

        except Exception as e:
            print(e)
            flash(f'Ошибка сохранения в БД :(\n\n{e}', 'flash-error')

        return redirect(url_for('admin'))

    return render_template('create_comp.html')


@application.route('/admin/create_rang', methods=['GET', 'POST'])
def create_rang():
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    rangs_database = RangsManager(USERS_DB)
    if request.method == 'POST':
        rang_name = request.form['rang-name']
        count = request.form['count']

        print("Отправленные данные:")
        print(rang_name, count)

        try:
            rangs_database.create_rang_competition_table()
            rangs_database.add_rang(rang_name, count)
            flash('Данные сохранены!', 'flash-success')
        except Exception as e:
            flash(f'Ошибка сохранения :(\n\n{e}', 'flash-error')
        return redirect(url_for('admin'))

    return render_template('create_rang.html')


@application.route('/admin/rangs', methods=['GET', 'POST'])
def rangs():
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    rangs_manager = RangsManager(USERS_DB)
    all_rangs = rangs_manager.view_rangs()
    return render_template("rangs.html", rangs_list=all_rangs)


@application.route('/admin/rang/<int:rang_id>/update', methods=['GET', 'POST'])
def rang_update(rang_id):
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        rangs_manager = RangsManager(USERS_DB)

        rang_name = request.form['rang-name']
        count = request.form['count']

        print("Отправленные данные:")
        print(rang_name, count)

        try:
            rangs_manager.update_rang(rang_id, rang_name, count)
            flash('Данные сохранены!', 'flash-success')
        except Exception as e:
            flash(f'Ошибка сохранения :(\n\n{e}', 'flash-error')
        return redirect(f'/admin/rang/{rang_id}')
    return render_template("rang.html")

@application.route('/admin/rang/<int:rang_id>/add', methods=['GET', 'POST'])
def rang_add_competition(rang_id):
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        rangs_manager = RangsManager(USERS_DB)

        eventID = request.form['protocol']
        if (not eventID.isdigit()):
            return
        event_managet = EventsDatabase(USERS_DB)
        #eventID = event_managet.get_event_by_id(competitionName)
        print("Отправленные данные:")
        print(rang_id, eventID)

        try:
            rangs_manager.add_competition_to_rang(rang_id, eventID)
            flash('Данные сохранены!', 'flash-success')
        except Exception as e:
            flash(f'Ошибка сохранения :(\n\n{e}', 'flash-error')
        return redirect(f'/admin/rang/{rang_id}')
    return render_template("rang.html")


@application.route('/admin/rang/<int:rang_id>', methods=['GET', 'POST'])
def view_rang_page_settings(rang_id):
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    rangs_manager = RangsManager(USERS_DB)
    elem_by_id = rangs_manager.get_rang_by_id(rang_id)
    return render_template("rang.html", rang=elem_by_id, id=rang_id)

@application.route('/rang/<int:rang_id>', methods=['GET', 'POST'])
def view_rang_page(rang_id):
    rangs_manager = RangsManager(USERS_DB)
    events = rangs_manager.get_rang_events(rang_id)
    name = rangs_manager.get_rang_name_by_id(rang_id)
    count = name[1]
    name = name[0]
    eventIDs = []
    for event in events:
        eventIDs.append(event[4])
    users_manager = UserManager(USERS_DB)
    eventIDs.sort()
    if (len(eventIDs) < 1):
        return redirect(url_for('index'))
    table_data = users_manager.get_users_with_events(eventIDs=eventIDs)
    table_data = preparation_data_to_rang_view(table_data, count)
    return render_template("rang_view.html", events=events, table_data=table_data, event_count=len(eventIDs), rang_name = name, count=count)

@application.route('/admin_login', methods=['GET', 'POST'])
def admin_login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'] 
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest() 
        login_manager = LoginManager(USERS_DB)
        user_id = login_manager.check_user_password(username=username, password=hashed_password)
        if (user_id > 0):
            session['user_id'] = user_id
            flash("Успешный вход!", 'flash-success')
            return redirect(url_for('admin'))
        else:
           error = 'Неправильное имя пользователя или пароль'
    return render_template("admin_login.html")


@application.route('/admin/logout', methods=['GET', 'POST'])
def admin_logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

def preparation_data_to_rang_view(table_data, count):
    data = []
    person_data = [0, [], '', '', '', '', 0]
    scores = []
    personID = 0
    for item in table_data:
        if (item[5] != personID and personID  != 0 ):
            if (len(scores) > count):
                person_data[1] = find_scores_not_accounting(person_data[3], scores.copy(), count)
                person_data[6] = get_sum_scores(scores, person_data[1])
            data.append(person_data)
            person_data = [0, [], '', '', '', '', 0]
            scores = []
        personID = item[5]
        person_data[0] = personID
        person_data[2] = item[0]
        person_data[3] = item[1]
        person_data[4] = item[2]
        person_data[5] = item[3]
        print(person_data)
        person_data.append(item[6])
        scores.append(item[7])
        person_data.append(item[7]) 
    if (len(scores) > count):
        person_data[1] = find_scores_not_accounting(person_data[3], scores.copy(), count)  
        person_data[6] = get_sum_scores(scores, person_data[1]) 
    data.append(person_data)
    data.sort(key=lambda data:(data[6]), reverse=True)
    data.sort(key=lambda data:(data[4]))
    return data
def find_scores_not_accounting(a, scores, count):
    scores_not_sort = scores.copy()
    scores.sort()
    find_indexes = []
    for i in range(0,len(scores)-count):
        index = scores_not_sort.index(scores[i])
        find_indexes.append(index)
        scores_not_sort[index] = ''
        scores[i] = ''
    find_indexes.sort()
    return find_indexes   

def  get_sum_scores(scores, not_accountig):
    sum = 0
    counter = 0
    for i in range(0, len(scores)):
        if (counter < len(not_accountig) and i == not_accountig[counter]):
            counter += 1
        else:
            sum += int(scores[i])   
    return sum

from manager_db import *
from competition_results import *
if __name__ == '__main__':
    application.run(debug=True, host='0.0.0.0')
