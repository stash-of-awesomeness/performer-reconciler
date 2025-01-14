from performer_reconciler.items import Performer
from scrapy.utils.project import get_project_settings
from stashapi.stashbox import StashBoxInterface
import scrapy


class StashdbSpider(scrapy.Spider):
    name = "stashdb"

    start_urls = ["data:text/plain,noop", ]

    def parse(self, _):
        settings = get_project_settings()

        self.stashdb = StashBoxInterface({
            "api_key": settings.get("STASHDB_API_KEY"),
        })

        

