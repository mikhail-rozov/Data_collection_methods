from pymongo import MongoClient
from pprint import pprint
from Lesson_8.Instaparser.spiders.instagram import InstagramSpider

client = MongoClient('localhost', 27017)
db = client.instagram

# 4) Написать запрос к базе, который вернет список подписчиков только указанного пользователя

# username = input('Введите имя пользователя для показа его подписчиков из базы: ')
username = InstagramSpider.user_1
for follower in db[username].followers.find({}, {'name': 1, '_id': 0}):
    pprint(follower['name'])

# 5) Написать запрос к базе, который вернет список профилей, на кого подписан указанный пользователь

# username = input('Введите имя пользователя для показа его подписок из базы: ')
username = InstagramSpider.user_2
for follow in db[username].following.find({}, {'profile_name': 1, '_id': 0}):
    pprint(follow['profile_name'])
