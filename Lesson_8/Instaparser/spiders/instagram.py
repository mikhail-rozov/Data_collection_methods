import scrapy
from scrapy.http import HtmlResponse
from Lesson_8.Instaparser.spiders.hidden_data import login, password
from Lesson_8.Instaparser.items import InstaparserItem
import re
from urllib.parse import urlencode
from copy import deepcopy


class InstagramSpider(scrapy.Spider):

    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    user_1 = 'data__science__guy'
    user_2 = 'machinelearningmath'
    users = [user_1, user_2]
    api_url = 'https://i.instagram.com/api/v1/friendships'
    api_header = {'User-Agent': 'Instagram 155.0.0.37.107'}

    def parse(self, response: HtmlResponse):

        # Достаём csrf-токен из html-кода:
        csrf = re.search(r'"csrf_token":"(\w+)"', response.text).group(1)

        yield scrapy.FormRequest(self.login_url,
                                 method='POST',
                                 callback=self.login_func,
                                 formdata={'username': login,
                                           'enc_password': password},
                                 headers={'X-CSRFToken': csrf})

    def login_func(self, response: HtmlResponse):
        j_data = response.json()
        if j_data['authenticated']:

            # Обходим всех пользователей:
            for user in self.users:
                yield response.follow('/' + user,
                                      callback=self.parse_user,
                                      cb_kwargs={'username': user})

    def parse_user(self, response: HtmlResponse, username):

        # Достаём id пользователя по его имени профиля из html-кода:
        user_id = re.search(rf'"id":"(\d+)","username":"{username}"', response.text).group(1)

        params = {'count': 12}

        # Обходим подписчиков и подписки пользователя:
        for follow_type in ('followers', 'following'):
            if follow_type == 'followers':
                params['search_surface'] = 'follow_list_page'

            yield response.follow(f'{self.api_url}/{user_id}/{follow_type}?{urlencode(params)}',
                                  callback=self.get_follows,
                                  headers=self.api_header,
                                  cb_kwargs={'user_id': user_id,
                                             'username': username,
                                             'params': deepcopy(params),
                                             'follow_type': follow_type})

    def get_follows(self, response: HtmlResponse, user_id, username, params, follow_type):
        j_data = response.json()
        if 'next_max_id' in j_data.keys():
            params['max_id'] = j_data['next_max_id']
            yield response.follow(f'{self.api_url}/{user_id}/{follow_type}?{urlencode(params)}',
                                  callback=self.get_follows,
                                  headers=self.api_header,
                                  cb_kwargs={'user_id': user_id,
                                             'username': username,
                                             'params': deepcopy(params),
                                             'follow_type': follow_type})
        follows = j_data['users']
        for follow in follows:
            item = InstaparserItem(username=username,
                                   type=follow_type,
                                   name=follow['full_name'] if follow['full_name']
                                   else follow['username'],
                                   profile_name=follow['username'],
                                   user_id=follow['pk'],
                                   photo_link=follow['profile_pic_url'])
            yield item
