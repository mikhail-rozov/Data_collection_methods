import scrapy
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient


class InstaparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client.instagram

    def process_item(self, item, spider):
        collection = self.db[item['username']]

        collection[item['type']].update_one({'user_id': item['user_id']}, {'$set': {'user_id': item['user_id'],
                                                                                    'name': item['name'],
                                                                                    'profile_name': item['profile_name'],
                                                                                    'photo': item['photo']}}, upsert=True)
        return item


class InstaPhotosPipeline(ImagesPipeline):

    def file_path(self, request, response=None, info=None, *, item=None):
        return f"{item['username']}/{item['type']}/{item['profile_name']}.jpg"

    def get_media_requests(self, item, info):
        if item['photo_link']:
            try:
                yield scrapy.Request(item['photo_link'])
            except Exception as err:
                print(err)

    def item_completed(self, results, item, info):
        if results:
            item['photo'] = results[0][1] if results[0][0] else item['photo_link']

        return item
