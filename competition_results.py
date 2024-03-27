from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import requests
from bs4 import BeautifulSoup
import sys
import os

from manager_db import USERS_DB, UserManager


# Создаем опции для Chrome
chrome_options = Options()
chrome_options.add_argument('--headless')  # Запускаем в headless режиме

# Создаем экземпляр WebDriver с указанными опциями
driver = webdriver.Chrome(options=chrome_options)

url = 'https://tverorient.su/doc/2023/2023-12-24/finish.html?scores=1'
driver.get(url)

results_tables = driver.find_element(By.ID, "results-tables")
table_text = results_tables.text

rows = table_text.split('\n')

table_data = []
for row in range(len(rows)):
    cells = rows[row].split()
    birth_date_index = next((index for index, value in enumerate(cells) if value.isdigit() and len(value) == 4), None)

    if birth_date_index is not None:
        team_elements = cells[3:birth_date_index]
        team_name = ' '.join(team_elements)
        cells[3] = team_name
    table_data.append(cells)


driver.quit()


users_data = []
buffer = []

table_name = None

for i in range(len(table_data)):
    if len(table_data[i]) == 3:
        if ',' in table_data[i][0]:
            table_name = table_data[i][0].replace(',', '')
            if buffer:
                users_data.append(buffer)
                buffer = []

    if table_data[i][0].isdigit():
        if table_data[i][0] == '1':
            users_data.append(buffer)
            buffer = []

        if table_data[i][-1].isdigit():
            line_data = table_name, table_data[i][0], table_data[i][1], table_data[i][2], table_data[i][3], table_data[i][-1]
        else:
            line_data = table_name, table_data[i][0], table_data[i][1], table_data[i][2], table_data[i][3], '0'
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
        user_manager.add_new_user(
            name_table="Результаты_01", lastname=user_cell[2], firstname=user_cell[3],
            team=user_cell[4], group_name=user_cell[0], scores=user_cell[5]
        )
