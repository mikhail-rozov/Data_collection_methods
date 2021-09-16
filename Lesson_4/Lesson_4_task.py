"""
1. Написать приложение, которое собирает основные новости с сайта на выбор lenta.ru, news.mail.ru, yandex-новости.
Для парсинга использовать XPath. Структура данных должна содержать:
название источника;
наименование новости;
ссылку на новость;
дата публикации.
2. Сложить собранные данные в БД
Минимум один сайт, максимум - все три
"""

from lxml import html
import requests
from pprint import pprint
import unicodedata
import datetime
from pymongo import MongoClient


def scrape_mail_ru():

    url = 'https://news.mail.ru/'
    response = requests.get(url, headers=headers)
    dom = html.fromstring(response.text)

    names = dom.xpath("//ul[contains(@class, 'list_half')]//li[@class='list__item']/a/text() | "
                      "//span[contains(@class, 'js-topnews__notification')]/text()")
    links = dom.xpath("//ul[contains(@class, 'list_half')]//li[@class='list__item']/a/@href | "
                      "//span[contains(@class, 'js-topnews__notification')]/../../@href")

    for i in range(len(names)):
        news_url = links[i]
        news_page = requests.get(news_url, headers=headers)
        page_dom = html.fromstring(news_page.text)
        source = page_dom.xpath("//div[contains(@class, 'breadcrumbs')]//span[@class='link__text']/text()")[0]
        published = page_dom.xpath("//span[contains(@class, 'js-ago')]/@datetime")
        published = datetime.datetime.strptime(published[0], '%Y-%m-%dT%H:%M:%S+03:00')
        published = published.strftime('%d-%m-%Y %H:%M')

        db.news.update_one({'_id': links[i]}, {'$set': {'_id': links[i],
                                                        'name': unicodedata.normalize('NFKD', names[i]),
                                                        'published': published,
                                                        'source': source}}, upsert=True)


def scrape_yandex():

    url = 'https://yandex.ru/news'
    response = requests.get(url, headers=headers)
    dom = html.fromstring(response.text)

    items = dom.xpath("//article[contains(@class, 'mg-grid__item')]")

    for item in items:
        name = unicodedata.normalize('NFKD', item.xpath(".//h2[@class='mg-card__title']/text()")[0])
        link = item.xpath(".//a[@class='mg-card__link']/@href")[0]
        published = item.xpath(".//span[@class='mg-card-source__time']/text()")[0]
        published = str(datetime.date.today()) + published
        published = datetime.datetime.strptime(published, '%Y-%m-%d%H:%M')
        published = published.strftime('%d-%m-%Y %H:%M')
        source = item.xpath(".//div[contains(@class, 'mg-card-footer')]//a/text()")[0]

        db.news.update_one({'_id': link}, {'$set': {'_id': link,
                                                    'name': unicodedata.normalize('NFKD', name),
                                                    'published': published,
                                                    'source': source}}, upsert=True)


if __name__ == '__main__':

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'}

    client = MongoClient('localhost', 27017)
    db = client['news']

    scrape_mail_ru()
    scrape_yandex()

    for el in db.news.find({}):
        pprint(el)
