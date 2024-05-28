# -*- coding: UTF-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import requests
from bs4 import BeautifulSoup
import sys
import os

from manager_db import USERS_DB, UserManager


class ManageResults:
    def __init__(self, protocol_link):
        self.protocol_link = protocol_link

    def __data_collection(self):
        # Создаем опции для Chrome
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Запускаем в headless режиме

        # Создаем экземпляр WebDriver с указанными опциями
        driver = webdriver.Chrome(options=chrome_options)

        url = self.protocol_link
        driver.get(url)

        results_tables = driver.find_element(By.ID, "results-tables")
        table_text = results_tables.text

        rows = table_text.split('\n')

        __table_data = []
        for row in range(len(rows)):
            cells = rows[row].split()
            print("!! ", cells)
            birth_date_index = next((index for index, value in enumerate(cells) if value.isdigit() and len(value) == 4), None)

            if birth_date_index is not None:
                team_elements = cells[3:birth_date_index]
                team_name = ' '.join(team_elements)
                cells[3] = team_name
            __table_data.append(cells)

        driver.quit()

        return __table_data

    def write_down_names_of_participants(self, event_id):
        table_data = self.__data_collection()
        score_array = [ 40, 37, 35, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1 ]
        users_data = []
        buffer = []

        table_name = None

        for i in range(len(table_data)):
            if len(table_data[i]) < 7  and not(str(table_data[i][0]).isdigit()):
                #if ',' in table_data[i][0]:
                table_name = ""
                for item in table_data[i]:
                    table_name += str(item) + " "
                if buffer:
                    users_data.append(buffer)
                    buffer = []

            if table_data[i][0].isdigit():
                if table_data[i][0] == '1':
                    users_data.append(buffer)
                    buffer = []
                score = 1
                last_index = len(table_data[i]) - 1
                place = 0
                if (str(table_data[i][last_index]).isdigit()):
                    place = int(table_data[i][last_index])
                if (int(place) <= len(score_array) and place != 0):
                    score = score_array[int(place)-1]
                else:
                    score = 0
                #if table_data[i][-1].isdigit():
                line_data = table_name, place, table_data[i][1], table_data[i][2], table_data[i][3], score
                #else:
                #    line_data = table_name, table_data[i][0], table_data[i][1], table_data[i][2], table_data[i][3], score
                buffer.append(line_data)

        if buffer:
            users_data.append(buffer)

        for user_row in users_data:
            for user_cell in user_row:
                print(user_cell)
            print()

        user_manager = UserManager(USERS_DB)

        for user_row in users_data:
            for user_cell in user_row:
                user_id = user_manager.find_users_in_db(firstname=user_cell[3], lastname=user_cell[2], group=user_cell[0])
                if (int(user_id) > 0):
                    user_manager.add_result_to_user(event_id=event_id, user_id=user_id, place=user_cell[1], score=user_cell[5])
                else:
                    user_id = user_manager.add_new_user(
                        lastname=user_cell[2], firstname=user_cell[3],
                        team=user_cell[4], group_name=user_cell[0])
                    user_manager.add_result_to_user(event_id=event_id, user_id=user_id, place=user_cell[1], score=user_cell[5])
