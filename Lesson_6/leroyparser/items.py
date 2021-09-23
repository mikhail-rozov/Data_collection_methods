# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst


def digitize(value):
    try:
        return int(value.replace(' ', ''))
    except (ValueError, TypeError):
        return None


def get_photos(value):
    return value.replace('w_82,h_82', 'w_2000,h_2000')


def get_features_values(value):
    return value.replace(r'\n', '').strip()


class LeroyparserItem(scrapy.Item):
    name = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field(input_processor=MapCompose(get_photos))
    features_keys = scrapy.Field()
    features_values = scrapy.Field(input_processor=MapCompose(get_features_values))
    features = scrapy.Field()
    link = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(digitize), output_processor=TakeFirst())
