import requests
from bs4 import BeautifulSoup


url = 'https://rufso.orgeo.ru/raiting/137'
response = requests.get(url)


if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    soup = BeautifulSoup(response.text, 'html.parser')

    all_links = soup.find_all('a')

    for link in all_links:
        href = link.get('href')
        if href:
            print(link.text)
else:
    print('Ошибка при получении страницы:', response.status_code)
