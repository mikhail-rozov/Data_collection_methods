# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient
import hashlib
from scrapy.utils.python import to_bytes

# Импортируем текст поискового запроса для разбивки скачанных файлов
# и коллекций базы данных по запросам.
from runner import query


class LeroyparserPipeline:

    def process_item(self, item, spider):

        # Обработаем характеристики товара, чтобы данные, независимо от их типа и количества, формировались
        # общим словарём (Задание 2):
        item['features'] = {}
        for i in range(len(item['features_keys'])):
            item['features'].update({item['features_keys'][i]: item['features_values'][i]})
        del item['features_keys']
        del item['features_values']

        return item


class LeroyPhotosPipeline(ImagesPipeline):

    # Переопределим метод класса ImagesPipeline для того, чтобы скачанные файлы
    # распределялись по папкам в зависимости от запроса (Задание 3).
    def file_path(self, request, response=None, info=None, *, item=None):
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        return f'{query}/{image_guid}.jpg'

    def get_media_requests(self, item, info):
        if item['photos']:
            try:
                for img_link in item['photos']:
                    yield scrapy.Request(img_link)
            except Exception as err:
                print(err)

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [photos[1] for photos in results if photos[0]]

        return item


class LeroyToMongoPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client.leroymerlin

    def process_item(self, item, spider):

        collection = self.db[query]
        collection.insert_one(dict(item))

        return item
