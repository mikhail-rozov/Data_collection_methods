# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import re
from pymongo import MongoClient

class BookparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.books

    def process_item(self, item, spider):
        if spider.name == 'book24':
            for key, value in item.items():
                if item[key]:
                    item[key] = value.replace(r'\n', '').replace('₽', '').strip()
        if not item['authors'] or 'не указано' in item['authors']:
            item['authors'] = None
        else:
            # Внутри ссылок на книги, к названиям прицепляются имена авторов,
            # причем на book24.ru это делается как-то выборочно. Уберём имена из названий:
            item['name'] = re.findall('^.*: (.*)', item['name'])[0] if ':' in item['name'] else item['name']
        item['base_price'] = self.digitize(int, item['base_price'])
        item['discounted_price'] = self.digitize(int, item['discounted_price'])
        item['rating'] = self.digitize(float, item['rating'])

        collection = self.mongobase[spider.name]
        collection.insert_one(dict(item))
        return item

    def digitize(self, func, expression):
        if not expression:
            return None
        expression = expression.replace(',', '.')
        try:
            return func(expression)
        except ValueError:
            return None
