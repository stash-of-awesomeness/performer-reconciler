from performer_reconciler.items import Performer, Scene, Studio, SourceReference, Gender

from datetime import datetime
from urllib.parse import urljoin
import scrapy


class SpunkWorthySpider(scrapy.Spider):
    name = "spunkworthy"
    result_prefix = "spunkworthy"
    allowed_domains = ["spunkworthy.com"]

    def start_requests(self):
        yield scrapy.http.Request(
            url="https://spunkworthy.com/preview/guys",
            callback=self.parse_performers,
        )

        yield scrapy.http.Request(
            url="https://spunkworthy.com/preview/videos",
            callback=self.parse_scenes,
        )

        yield scrapy.http.Request(
            url="https://spunkworthy.com/preview/bonus",
            callback=self.parse_scenes,
        )

        yield Studio(
            source_reference="spunkworthy",
            source_name="spunkworthy",

            name="SpunkWorthy",
            urls=[
                "https://spunkworthy.com",
            ],
        )

    def _next_url(self, response):
        url_element = response.css(".pagination a.next_page")

        if not url_element:
            return None

        return urljoin(response.url, url_element.attrib["href"])

    def parse_performers(self, response):
        for performer in response.css(".content.posters .hs > a"):
            yield scrapy.http.Request(
                url=urljoin(response.url, performer.attrib["href"].split("?")[0]),
                callback=self.parse_performer,
            )

        if next_url := self._next_url(response):
            yield scrapy.http.Request(
                url=next_url,
                callback=self.parse_performers,
            )

    def parse_performer(self, response):
        yield Performer(
            source_reference=response.url.rsplit("/", 1)[1],
            source_name="spunkworthy",

            name=response.css(".head .h1 .h2::text").get(),
            gender=Gender.MALE,

            image_url=urljoin(response.url, response.css(".model_left img").attrib["src"]),

            urls=[
                response.url,
            ],
        )

    def parse_scenes(self, response):
        for performer in response.css(".content.posters .vid"):
            scene_date = scrapy.Selector(text=performer.xpath("comment()").get().replace("<!--", "").replace("-->", "")).css("span::text").get()
            scene_date = datetime.strptime(scene_date, "%d %b %y").date()

            yield scrapy.http.Request(
                url=urljoin(response.url, performer.css("p > a").attrib["href"].split("?")[0]),
                callback=self.parse_scene,
                meta={
                    "scene_date": scene_date,
                }
            )

        if next_url := self._next_url(response):
            yield scrapy.http.Request(
                url=next_url,
                callback=self.parse_scenes,
            )

    def parse_scene(self, response):
        video_player = response.css("#player video")

        if video_player:
            cover_image = video_player.attrib["poster"]
        else:
            cover_image = urljoin(response.url, response.css(".video_player > img")[0].attrib["src"])

        if detail_paragraphs := response.css(".vid_text > p::text").getall():
            scene_details = "\n\n".join(detail_paragraphs)
        else:
            scene_details = "\n\n".join(response.css(".video_synopsis > p::text").getall())

        performers = []

        for performer in response.css(".content.posters .hs > a"):
            performers.append(
                SourceReference(
                    source_reference=performer.attrib["href"].rsplit("/", 1)[1],
                    source_name="spunkworthy",
                )
            )

        yield Scene(
            source_reference=response.url.rsplit("/", 1)[1],
            source_name="spunkworthy",

            title=response.css(".head .h1 .h2::text").get(),
            details=scene_details,

            studio=SourceReference(
                source_reference="spunkworthy",
                source_name="spunkworthy",
            ),
            performers=performers,

            release_date=response.meta["scene_date"],

            cover_image_url=cover_image,
            urls=[
                response.url,
            ],
        )

        for performer in response.css(".content.posters .hs > a"):
            yield scrapy.http.Request(
                url=urljoin(response.url, performer.attrib["href"].split("?")[0]),
                callback=self.parse_performer,
            )
