from performer_reconciler.items import Performer
from stashapi.stashbox import StashBoxInterface
import scrapy


class StashdbSpider(scrapy.Spider):
    name = "stashdb"

    def start_requests(self):
        self.stashdb = StashBoxInterface()

