import os
import sqlite3


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
    "scores"
]


class UserManager:
    def __init__(self, name_db):
        self.name_db = name_db

    def add_new_user(self, name_table, lastname, firstname, team, group_name, scores):
        """
            Алгоритм добавления пользователей в БД
        """
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
            print("data:", lastname, firstname, team, group_name, scores)
            print(f"insert_fields: {insert_fields}; place_items: {place_items}")

            _connect = sqlite3.connect(self.name_db)
            _c = _connect.cursor()

            check_table = self.check_exist_table(name_table)
            print(group_name)
            if check_table is False:
                _c.execute(f'''
                        CREATE TABLE IF NOT EXISTS {name_table} (
                            id INTEGER PRIMARY KEY,
                            lastname TEXT,
                            firstname TEXT,
                            team TEXT,
                            group_name TEXT,
                            scores TEXT
                        )
                    ''')
                _connect.commit()

            _c.execute(f'INSERT INTO {name_table} ({insert_fields}) VALUES ({place_items})',
                       (lastname, firstname, team, group_name, scores))
            _connect.commit()
            _connect.close()
            print("---------- OK ----------")

        except Exception as e:
            print("---------- ERROR ----------")
            print(f"----- {e} add_new_user -----")

    def check_user_in_database(self, user_id):
        __connect = sqlite3.connect(self.name_db)
        __cursor = __connect.cursor()

        __cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        result = __cursor.fetchone()

        __cursor.close()
        __connect.close()

        if result:
            return True
        else:
            return False

    def find_users_in_db(self, id_user):
        """
            Поиск и выгрузка данных о пользователе из БД
            id_user - идентификатор пользователя.
            user_id или fullname.
        """
        __cursor = sqlite3.connect(self.name_db).cursor()
        __cursor.execute("SELECT * FROM users WHERE id = ?", (id_user,))
        find_users = __cursor.fetchone()

        result = ''
        if find_users:
            for item in find_users:
                result += f"{item} "
            return result
        else:
            __cursor.execute("SELECT * FROM users WHERE fullname = ?", (id_user,))
            fetch_by_name = __cursor.fetchall()
            if fetch_by_name:
                if 0 < len(fetch_by_name) < 2:
                    for items in fetch_by_name:
                        for item in items:
                            result += f"{item} "
                else:
                    for items in fetch_by_name:
                        for item in items:
                            result += f"{item} "
                        result += '\n'
                return result
            else:
                return False

    def load_all_users(self):
        """
            Display data about users from database
            Only print
            return: None
        """

        connect = sqlite3.connect(self.name_db)
        cursor = connect.cursor()

        cursor.execute("SELECT * FROM users")
        all_users = cursor.fetchall()

        for user in all_users:
            for i in range(len(user)):
                if i == len(user) - 1:
                    print(user[i], end="")
                else:
                    print(user[i], end=" --- ")
            print()

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

    def check_exist_table(self, name_table):
        __connect = sqlite3.connect(self.name_db)
        __cursor = __connect.cursor()
        __cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{name_table}'")
        table_exists = __cursor.fetchone() is not None

        __connect.commit()
        __connect.close()

        return table_exists
