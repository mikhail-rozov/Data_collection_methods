from bs4 import BeautifulSoup
import pandas as pd
import requests
from fake_headers import Headers
import re
import unicodedata


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
            min_salary.append(sal.split('–')[0].strip())
            max_salary.append(sal.split('–')[1].strip())
        elif 'от' in sal:
            min_salary.append(sal.split()[1])
            max_salary.append(None)
        elif 'до' in sal:
            min_salary.append(None)
            max_salary.append(sal.split()[1])
        else:
            min_salary.append(None)
            max_salary.append(None)

    vacancies_list = []
    for i in range(len(vacancies_name)):
        vacancies_list.append({
            'name': vacancies_name[i],
            'url': vacancies_url[i],
            'MIN salary': min_salary[i],
            'MAX salary': max_salary[i],
            'Website': 'HH.ru'}
        )
    return vacancies_list


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
            min_salary.append(sal.split('—')[0])
            max_salary.append(sal.split('—')[1])
        elif 'от' in sal:
            min_salary.append(sal.replace('от', ''))
            max_salary.append(None)
        elif 'договор' in sal:
            min_salary.append(None)
            max_salary.append(None)
        else:
            min_salary.append(None)
            max_salary.append(sal.replace('до', ''))

    vacancies_list = []
    for i in range(len(vacancies_name)):
        vacancies_list.append({
            'name': vacancies_name[i],
            'url': vacancies_url[i],
            'MIN salary': min_salary[i],
            'MAX salary': max_salary[i],
            'Website': 'Superjob.ru'}
        )
    return vacancies_list


def parse_all(search_string, page):
    header = Headers(
        browser='chrome',
        os='win',
        headers=False)

    span_hh = parse_hh(search_string.replace(' ', '+'), page, header)
    span_superjob = parse_superjob(search_string.replace(' ', '%20'), page, header)

    return span_hh + span_superjob


if __name__ == '__main__':

    search_string = input('Какую вакансию ищем? ')

    all_vacancies = []
    for i in range(3):
        all_vacancies += parse_all(search_string, i)

    pd.DataFrame(all_vacancies).to_json('./vacancies.json', force_ascii=False, indent=4)
    pd.set_option('display.max_columns', 20)
    pd.set_option('display.max_rows', 200)
    pd.set_option('display.width', 1200)
    pd.set_option('display.max_colwidth', 200)
    print(pd.read_json('./vacancies.json'))
