from scrapy.settings import Settings
from scrapy.crawler import CrawlerProcess
from Lesson_5.bookparser import settings
from Lesson_5.bookparser.spiders.labirint import LabirintSpider
from Lesson_5.bookparser.spiders.book24 import Book24Spider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(crawler_settings)
    process.crawl(LabirintSpider)
    process.crawl(Book24Spider)

    process.start()
