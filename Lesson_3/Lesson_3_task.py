"""
1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию,
записывающую собранные вакансии в созданную БД.
2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы.
3. Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта.
"""

# В данном задании будем работать с кодом, написанным в уроке № 2, где мы собирали информацию о вакансиях.
import pymongo.errors
from bs4 import BeautifulSoup
import requests
from fake_headers import Headers
import re
import unicodedata
from pymongo import MongoClient
from pprint import pprint


def parse_hh(search_string, page, header):
    url = f'https://hh.ru/search/vacancy?clusters=true&ored_clusters=' \
          f'true&enable_snippets=true&salary=&st=searchVacancy&text={search_string}&page={page}'
    response = requests.get(url, headers=header.generate()).text
    soup = BeautifulSoup(response, 'lxml')
    vacancies_name = [unicodedata.normalize('NFKD', i.text) for i in
                      soup.select('div.vacancy-serp-item span a.bloko-link')]
    vacancies_url = ['https://hh.ru/vacancy/' + re.findall(r'(\d+)\D+', i['href'])[0] for i in
                     soup.select('div.vacancy-serp-item span.g-user-content a.bloko-link')]
    vacancies_salary = []

    for vacancy in soup.select('div.vacancy-serp-item'):
        vacancies_salary.append(str(re.findall(r'tion\">(.+)руб\.', str(vacancy))).replace(r'\u202f', ''))

    min_salary = []
    max_salary = []

    for salary in vacancies_salary:
        sal = salary.replace("['", "").replace("']", "")
        if '–' in sal:
            min_salary.append(int(sal.split('–')[0].strip()))
            max_salary.append(int(sal.split('–')[1].strip()))
        elif 'от' in sal:
            min_salary.append(int(sal.split()[1]))
            max_salary.append(None)
        elif 'до' in sal:
            min_salary.append(None)
            max_salary.append(int(sal.split()[1]))
        else:
            min_salary.append(None)
            max_salary.append(None)

    for i in range(len(vacancies_name)):
        # Согласно условию задания № 3 добавляем только новые вакансии с сайта. Для добавления всех
        # вакансий с дублированием существующих надо заменить поле '_id' в словаре ниже на 'url'.
        try:
            vacancies.insert_one({'_id': vacancies_url[i],
                                  'name': vacancies_name[i],
                                  'MIN salary': min_salary[i],
                                  'MAX salary': max_salary[i],
                                  'Website': 'HH.ru'})
        except pymongo.errors.DuplicateKeyError:
            continue


def parse_superjob(search_string, page, header):
    url = f'https://russia.superjob.ru/vacancy/search/?keywords={search_string}&page={page + 1}'
    response = requests.get(url, headers=header.generate()).text
    soup = BeautifulSoup(response, 'lxml')
    vacancies_name = [i.text for i in soup.select('div.f-test-search-result-item a._6AfZ9')]

    vacancies_url = ['https://superjob.ru' + i['href'] for i in soup.select('div.f-test-search-result-item a._6AfZ9')]

    vacancies_salary = [unicodedata.normalize('NFKD', i.text) for i in
                        soup.select('span.f-test-text-company-item-salary')]

    min_salary = []
    max_salary = []

    for salary in vacancies_salary:
        sal = salary.replace('руб./месяц', '').replace(' ', '')
        if '—' in sal:
            min_salary.append(int(sal.split('—')[0]))
            max_salary.append(int(sal.split('—')[1]))
        elif 'от' in sal:
            min_salary.append(int(sal.replace('от', '')))
            max_salary.append(None)
        elif 'договор' in sal:
            min_salary.append(None)
            max_salary.append(None)
        else:
            min_salary.append(None)
            max_salary.append(int(sal.replace('до', '')))

    for i in range(len(vacancies_name)):
        try:
            vacancies.insert_one({'_id': vacancies_url[i],
                                  'name': vacancies_name[i],
                                  'MIN salary': min_salary[i],
                                  'MAX salary': max_salary[i],
                                  'Website': 'Superjob.ru'})
        except pymongo.errors.DuplicateKeyError:
            continue


def parse_all(search_string, page):
    header = Headers(
        browser='chrome',
        os='win',
        headers=False)

    parse_hh(search_string.replace(' ', '+'), page, header)
    parse_superjob(search_string.replace(' ', '%20'), page, header)


if __name__ == '__main__':

    client = MongoClient('127.0.0.1', 27017)
    db = client['vacancies']
    vacancies = db.vacancies

    search_string = input('Какую вакансию добавить в базу? ')
    salary_threshold = int(input('Вывести на экран вакансии с заработной платой больше какой величины?: '))

    for i in range(3):
        parse_all(search_string, i)

    for item in vacancies.find({'$or': [{'MIN salary': {'$gte': salary_threshold}},
                                        {'MAX salary': {'$gte': salary_threshold}}]}):
        pprint(item)
