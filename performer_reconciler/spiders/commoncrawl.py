import scrapy


class CommonCrawlSpider(scrapy.Spider):
    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            "performer_reconciler.middlewares.CommonCrawlMiddleware": 900,
            "scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware": None,
        },
    }
