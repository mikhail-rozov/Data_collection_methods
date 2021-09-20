import scrapy
from scrapy.http import HtmlResponse
from Lesson_5.bookparser.items import BookparserItem


class Book24Spider(scrapy.Spider):
    name = 'book24'
    allowed_domains = ['book24.ru']
    start_urls = ['https://book24.ru/search/page-1/?q=%D0%B8%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F']
    i = 1

    def parse(self, response: HtmlResponse):

        urls = response.xpath("//div[@class='product-list__item']//"
                              "a[contains(@class, 'product-card__name')]/@href").getall()
        if urls:
            for url in urls:
                yield response.follow(url, callback=self.parse_book)

            self.i += 1
            next_page = f'https://book24.ru/search/page-{self.i}/?q=%D0%B8%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F'
            yield response.follow(next_page, callback=self.parse)

    def parse_book(self, response: HtmlResponse):
        name = response.xpath("//h1/text()").get()
        link = response.url
        authors = response.xpath("//div[@class='product-characteristic__value']//text()").get()
        base_price = response.xpath("//span[contains(@class, 'product-sidebar-price__price')]/text()").get()
        discounted_price = response.xpath("//span[contains(@class, 'product-sidebar-price__price')]/text()")[2].get() \
            if response.xpath("//span[@class='product-sidebar-price__discount']") else None
        rating = response.xpath("//span[@class='rating-widget__main-text']/text()").get()
        item = BookparserItem(name=name, link=link, authors=authors, base_price=base_price,
                              discounted_price=discounted_price, rating=rating)
        yield item
