# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BookparserItem(scrapy.Item):
    name = scrapy.Field()
    link = scrapy.Field()
    authors = scrapy.Field()
    base_price = scrapy.Field()
    discounted_price = scrapy.Field()
    rating = scrapy.Field()

