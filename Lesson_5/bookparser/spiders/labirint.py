import scrapy
from scrapy.http import HtmlResponse
from Lesson_5.bookparser.items import BookparserItem


class LabirintSpider(scrapy.Spider):
    name = 'labirint'
    allowed_domains = ['labirint.ru']
    start_urls = ['https://www.labirint.ru/search/%D0%B8%D1%81%D1%82%D0%BE%D1%80%D0%B8%D1%8F/']

    def parse(self, response: HtmlResponse):
        urls = response.xpath("//a[@class='product-title-link']/@href").getall()
        next_page = response.xpath("//div[@class='pagination-next']/a/@href").get()

        if next_page:
            yield response.follow(next_page, callback=self.parse)

        for url in urls:
            yield response.follow(url, callback=self.parse_book)

    def parse_book(self, response: HtmlResponse):
        name = response.xpath("//h1/text()").get()
        link = response.url
        authors = response.xpath("//a[@data-event-label='author']/text()").getall()
        base_price = response.xpath("//span[@class='buying-priceold-val-number']/text()").get()
        discounted_price = response.xpath("//span[@class='buying-pricenew-val-number']/text()").get()
        rating = response.xpath("//div[@id='rate']/text()").get()
        item = BookparserItem(name=name, link=link, authors=authors, base_price=base_price,
                              discounted_price=discounted_price, rating=rating)
        yield item
