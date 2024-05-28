# -*- coding: UTF-8 -*-
import os
import sqlite3
import hashlib

from time import time


__version__ = '0.2.0'


USERS_DB = 'competitions.db'


if os.path.exists(USERS_DB) is False:
    print("=*=*=*=*=*=* WARNING =*=*=*=*=*=*")
    print(f"---- CREATE DATABASE ({USERS_DB}) ----")
    conn = sqlite3.connect(USERS_DB)
    c = conn.cursor()
    conn.commit()
    conn.close()
    print("----------- SUCCSES -----------")


name_fields_for_users = [
    "lastname",
    "firstname",
    "team",
    "group_name",
]


class ManagerDataBase:
    def __init__(self, name_db):
        self.name_db = name_db


    def check_exist_table(self, name_table):
        __connect = sqlite3.connect(self.name_db)
        __cursor = __connect.cursor()

        __cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{name_table}'")
        table_exists = __cursor.fetchone() is not None

        __connect.commit()
        __connect.close()

        return table_exists

    def check_by_id_in_database(self, table_name, __id):
        __connect = sqlite3.connect(self.name_db)
        __cursor = __connect.cursor()

        __cursor.execute(f"SELECT * FROM {table_name} WHERE id = ?", (__id,))
        result = __cursor.fetchone()

        __cursor.close()
        __connect.close()

        if result:
            return True
        else:
            return False



class UserManager(ManagerDataBase):
    def create_database(self):
        _connect = sqlite3.connect(self.name_db)
        _c = _connect.cursor()
        check_table = self.check_exist_table("persons")
        if check_table is False:
            _c.execute(f'''
                    CREATE TABLE IF NOT EXISTS persons (
                        id INTEGER PRIMARY KEY,
                        firstname TEXT,
                        lastname TEXT, 
                        year_birth INTEGER,
                        group_name TEXT,
                        team TEXT
                    )
                ''')
            _connect.commit()

        _c.close()
        _connect.close()
    def add_new_user(self, lastname, firstname, team, group_name):
        """
            Алгоритм добавления пользователей в БД
        """
        check_table = self.check_exist_table("persons")
        if check_table is False:
            self.create_database()
        try:
            global name_fields_for_users
            insert_fields, place_items = "", ""

            for i in range(len(name_fields_for_users)):
                if i == len(name_fields_for_users) - 1:
                    insert_fields += name_fields_for_users[i]
                    place_items += "?"
                else:
                    insert_fields += f"{name_fields_for_users[i]}, "
                    place_items += "?, "

            print("\nusers_manager.py: UserManager -> add_new_user")
            print("data:", lastname, firstname, team, group_name)
            print(f"insert_fields: {insert_fields}; place_items: {place_items}")

            _connect = sqlite3.connect(self.name_db)
            _c = _connect.cursor()



            _c.execute(f'INSERT INTO persons ({insert_fields}) VALUES ({place_items})',
                       ( lastname, firstname, team, group_name))
            _connect.commit()
            user_id = _c.lastrowid
            _c.close()
            _connect.close()
            print("---------- OK ----------")
            return int(user_id)

        except Exception as e:
            print("---------- ERROR ----------")
            print(f"----- {e} add_new_user -----")
    
    def add_result_to_user(self, event_id, user_id, place, score):
        _connect = sqlite3.connect(self.name_db)
        _c = _connect.cursor()
        _c.execute(f"INSERT INTO results (eventID, personID, place, score) VALUES (?, ?, ?, ?)", (event_id, user_id, place, score))
        _connect.commit()
        _c.close()
        _connect.close()

    def find_users_in_db(self, firstname, lastname, group):
        """
            Поиск и выгрузка данных о пользователе из БД
            id_user - идентификатор пользователя.
            user_id или fullname.
        """
        check_table = self.check_exist_table("persons")
        if check_table is False:
            self.create_database()
        __cursor = sqlite3.connect(self.name_db).cursor()
        __cursor.execute("SELECT id FROM persons WHERE firstname = ? AND lastname = ? AND group_name = ?", (firstname, lastname, group))
        find_users = __cursor.fetchone()

        if find_users is None:
            return -1
        else:
            return find_users[0]

    def load_all_users(self, table_name, display=False):
        """
            Display data about users from database
            Only print
            return: None
        """

        connect = sqlite3.connect(self.name_db)
        cursor = connect.cursor()

        cursor.execute(f"SELECT * FROM {table_name}")
        all_users = cursor.fetchall()

        if display:
            for user in all_users:
                for i in range(len(user)):
                    if i == len(user) - 1:
                        print(user[i], end="")
                    else:
                        print(user[i], end=" --- ")
                print()
        return all_users

    def read_users_from_db(self, table):
        """
            Return all data about users from DB.
            return: list()
        """
        connect = sqlite3.connect(self.name_db)
        cursor = connect.cursor()

        cursor.execute(f"SELECT * FROM {table}")
        all_users = cursor.fetchall()

        cursor.close()
        connect.close()

        return all_users
    
    def get_users_with_events(self, eventIDs):
        param_str = ""
        for item in eventIDs:
            param_str += str(item) + ","
        param_str = param_str[:-1]
        connect = sqlite3.connect(self.name_db)
        cursor = connect.cursor()
        cursor.execute(f"SELECT firstname, lastname, group_name, team, eventID, personID, place, score FROM results LEFT JOIN persons ON results.personID = persons.ID where eventID IN ({param_str}) ORDER by personID, eventID")
        return cursor.fetchall()
        


class EventsDatabase(ManagerDataBase):
    def add_event(self, event_name, discipline, date, protocol_link):
        table_name_events = 'events'

        __connect = sqlite3.connect(self.name_db)
        __cursor = __connect.cursor()
        event_id = 0
        check_table = self.check_exist_table("results")
        if check_table is False:
            __cursor.execute(f'''
                    CREATE TABLE IF NOT EXISTS results (
                        id INTEGER PRIMARY KEY,
                        eventID INTEGER,
                        personID INTEGER,
                        place INTEGER,
                        score INTEGER
                    )
                ''')
            __connect.commit()

        check_table = self.check_exist_table(table_name_events)
        if check_table is False:
            __cursor.execute(f'''
                    CREATE TABLE IF NOT EXISTS {table_name_events} (
                        id INTEGER PRIMARY KEY,
                        event_name TEXT,
                        discipline TEXT,
                        date TEXT,
                        protocol_link TEXT
                    )
                ''')
            __connect.commit()

        __cursor.execute(f'''
            INSERT INTO {table_name_events} (event_name, discipline, date, protocol_link)
            VALUES (?, ?, ?, ?)
        ''', (event_name, discipline, date, protocol_link))
        __connect.commit()
        event_id = __cursor.lastrowid
        __cursor.close()
        __connect.close()
        return event_id

    def view_events(self):
        check_table = self.check_exist_table('events')
        if check_table:
            __connect = sqlite3.connect(self.name_db)
            __cursor = __connect.cursor()

            __cursor.execute("SELECT * FROM events")
            all_events = __cursor.fetchall()

            __cursor.close()
            __connect.close()

            return all_events
        
    def get_event_by_id(self, eventName):
        __connect = sqlite3.connect(self.name_db)
        __cursor = __connect.cursor()
        __cursor.execute(f"SELECT id FROM events WHERE event_name=\"{eventName}\"")
        eventID = __cursor.fetchone()[0]
        __cursor.close()
        __connect.close()
        return eventID
    
    def get_united_statistics(self, eventsIdArray):
        __connect = sqlite3.connect(self.name_db)
        __cursor = __connect.cursor()
        __cursor.execute(f'''CREATE TABLE IF NOT EXIST TEMP_RANG_STATISTICS (
                         
                         )
                         ''')
        pass


class RangsManager(ManagerDataBase):
    def create_rang_competition_table(self):
        __connect = sqlite3.connect(self.name_db)
        __cursor = __connect.cursor()
        __cursor.execute(f'''
                    CREATE TABLE IF NOT EXISTS RANGS_COMPETITIONS (
                        rangID INTEGER,
                        competitionID INTEGER
                    )
                ''')
        print("success")
        __connect.commit()
        __cursor.close()
        __connect.close()
    def add_rang(self, rang_name, count):
        table_name_events = 'rangs'

        __connect = sqlite3.connect(self.name_db)
        __cursor = __connect.cursor()

        check_table = self.check_exist_table(table_name_events)
        if check_table is False:
            __cursor.execute(f'''
                    CREATE TABLE IF NOT EXISTS {table_name_events} (
                        id INTEGER PRIMARY KEY,
                        rang_name TEXT,
                        count INTEGER
                    )
                ''')
            __connect.commit()

        __cursor.execute(f'''
            INSERT INTO {table_name_events} (rang_name, count)
            VALUES (?, ?)
        ''', (rang_name, count))
        __connect.commit()

        __cursor.close()
        __connect.close()

    def view_rangs(self):
        check_table = self.check_exist_table('rangs')
        if check_table:
            __connect = sqlite3.connect(self.name_db)
            __cursor = __connect.cursor()
            __cursor.execute("SELECT id, rang_name FROM rangs")
            all_rangs = __cursor.fetchall()

            __cursor.close()
            __connect.close()

            return all_rangs

    def get_rang_by_id(self, id):
        check_table = self.check_exist_table('rangs')
        if check_table:
            __connect = sqlite3.connect(self.name_db)
            __cursor = __connect.cursor()

            __cursor.execute("SELECT rang_name, count FROM rangs WHERE id=?", (id,))
            all_rangs = __cursor.fetchall()

            __cursor.close()
            __connect.close()

            return all_rangs

    def update_rang(self, id, name, count) -> None:
        check_table = self.check_exist_table('rangs')
        if check_table:
            __connect = sqlite3.connect(self.name_db)
            __cursor = __connect.cursor()

            __cursor.execute("UPDATE rangs SET rang_name=?, count=? WHERE id=?", (name, count, id))
            __connect.commit()

            __cursor.close()
            __connect.close()
    
    def add_competition_to_rang(self, rangID, competitionID):
        __connect = sqlite3.connect(self.name_db)
        __cursor = __connect.cursor()
        __cursor.execute("INSERT INTO RANGS_COMPETITIONS (rangID, competitionID) VALUES (?, ?)", (rangID, competitionID))
        __connect.commit()
        __cursor.close()
        __connect.close()
        
    def get_rang_events(self, rang_id):
        __connect = sqlite3.connect(self.name_db)
        __cursor = __connect.cursor()
        __cursor.execute(f"SELECT competitionID FROM RANGS_COMPETITIONS WHERE rangID={rang_id}")
        events = __cursor.fetchall()
        events_data = []
        for event in events:
            __cursor.execute(f"SELECT date, event_name, discipline, protocol_link, id FROM events WHERE id={event[0]}")
            events_data.append(__cursor.fetchone())
        __cursor.close()
        __connect.close()
        return events_data
    
    def get_rang_name_by_id(self, rang_id):
        __connect = sqlite3.connect(self.name_db)
        __cursor = __connect.cursor()
        __cursor.execute(f"SELECT rang_name, count FROM rangs WHERE ID=?",(rang_id,))
        name = __cursor.fetchone()
        if name is None:
            return ""
        else:
            return name
        

class LoginManager(ManagerDataBase):
    def create_tables(self):
        __connect = sqlite3.connect(self.name_db)
        __cursor = __connect.cursor()
        __cursor.execute(f"CREATE TABLE IF NOT EXISTS login_data (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)")
        __connect.commit()
        self.create_user('admin', 'adminarztop43')
        __connect.commit()
        __connect.close()

    def create_user(self, username, password):
        check_table = self.check_exist_table('login_data')
        if not check_table:
            self.create_tables()
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        __connect = sqlite3.connect(self.name_db)
        __cursor = __connect.cursor()
        __cursor.execute("INSERT INTO login_data (username, password) VALUES (?, ?)", (username, hashed_password))
        __connect.commit()
        __connect.close()
    
    def check_user_password(self, username, password):
        check_table = self.check_exist_table('login_data')
        if not check_table:
            self.create_tables()
        __connect = sqlite3.connect(self.name_db)
        __cursor = __connect.cursor()
        user = __cursor.execute("SELECT * FROM login_data WHERE username = ?", (username,)).fetchone()
        if user and user[2] == password:
            return user[0]
        else:
            return -1