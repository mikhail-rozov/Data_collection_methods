import scrapy
from scrapy.http import HtmlResponse
from Lesson_6.leroyparser.items import LeroyparserItem
from scrapy.loader import ItemLoader


class LeroymerlinSpider(scrapy.Spider):
    name = 'leroymerlin'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, search_string, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [f'https://leroymerlin.ru/search/?q={search_string}']
        self.i = 1

    def parse(self, response: HtmlResponse):

        # При попытке перехода на номер страницы, превышающий максимальный, сайт перенаправляет
        # нас на последнюю страницу. То есть, в этом случае, мы получаем не 200 статус, а 300 серию.
        # Поэтому статус, отличный от 200, будет нашим выходом из цикла.
        if response.status == 200:
            urls = response.xpath("//a[@data-qa='product-name']")
            for url in urls:
                yield response.follow(url, callback=self.parse_product)

            self.i += 1
            next_page = self.start_urls[0] + f'&page={self.i}'
            yield response.follow(next_page, callback=self.parse)

    def parse_product(self, response: HtmlResponse):

        loader = ItemLoader(item=LeroyparserItem(), response=response)

        loader.add_xpath('name', "//h1/text()")
        loader.add_xpath('photos', "//img[@slot='thumbs']/@src")
        loader.add_xpath('features_keys', "//dt[@class='def-list__term']/text()")
        loader.add_xpath('features_values', "//dd[@class='def-list__definition']/text()")
        loader.add_value('link', response.url)
        loader.add_xpath('price', "//span[@slot='price']/text()")

        yield loader.load_item()
