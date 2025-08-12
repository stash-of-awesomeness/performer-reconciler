from performer_reconciler.items import Link, LinkQuality, LinkSite, Performer, Scene, Studio, SourceReference, Gender

from datetime import datetime
from urllib.parse import urljoin
import scrapy


class LibertyMediaSpider(scrapy.Spider):

    def start_requests(self):
        yield scrapy.http.Request(
            url=f"{self.model_prefix}/1/name/",
            callback=self.parse_performers,
        )

        for category in self.scene_categories:
            yield scrapy.http.Request(
                url=f"{self.trailer_prefix}/categories/{category}/1/name/",
                callback=self.parse_category,
            )

        yield Studio(
            source_reference=self.name,
            source_name=self.result_prefix,

            name=self.name,
            urls=[
                Link(
                    site=LinkSite.HOME_PAGE,
                    quality=LinkQuality.SOURCE,
                    url=self.trailer_prefix.split(".com")[0] + ".com",
                )
            ]
        )

    def _id_from_url(self, url):
        return url.rsplit("/")[-1].split(".")[0]

    def parse_category(self, response):
        for scene in response.css(".container .items.update-items .item.item-update a[title]"):
            yield scrapy.http.Request(
                url=urljoin(response.url, scene.attrib["href"]),
                callback=self.parse_scene,
            )

        if next_url := response.css("a.next-page"):
            yield scrapy.http.Request(
                url=next_url.attrib["href"],
                callback=self.parse_category,
            )

    def parse_scene(self, response):
        release_date = response.css(".added::text").getall()[1].split("|")[0].strip()
        duration = response.css(".added::text").getall()[2].split("|")[0].replace("Minutes", "").strip()

        if ":" not in duration:
            duration = 0
        else:
            if duration.count(":") == 1:
                minutes, seconds = duration.split(":")
                duration = int(minutes) * 60 + int(seconds)
            else:
                hours, minutes, seconds = duration.split(":")
                duration = int(hours) * 3600 + int(minutes) * 60 + int(seconds)

        details = response.css(".description p::text").get()
        if details:
            details = details.strip()

        scene = Scene(
            source_name=self.result_prefix,
            source_reference=self._id_from_url(response.url),

            studio=SourceReference(
                source_reference=self.result_prefix,
                source_name=self.result_prefix,
            ),

            title=response.css("h1::text").get().strip(),
            details=details,
            duration=duration,

            cover_image_url=response.css(".player-thumb .stdimage").attrib.get("src0_1x"),

            release_date=datetime.strptime(
                release_date,
                "%B %d, %Y",
            ).date(),

            urls=[
                Link(
                    site=LinkSite.STUDIO,
                    quality=LinkQuality.SOURCE,
                    url=response.url,
                )
            ],
        )

        for performer in response.css(".modelFeaturing ul > li > a"):
            scene.performers.append(
                SourceReference(
                    source_name=self.result_prefix,
                    source_reference=self._id_from_url(performer.attrib["href"]),
                )
            )

            yield scrapy.http.Request(
                url=performer.attrib["href"],
                callback=self.parse_performer,
            )

        yield scene

    def parse_performers(self, response):
        for performer in response.css(".container .items.model-items .item.item-model a[title]"):
            yield scrapy.http.Request(
                url=performer.attrib["href"],
                callback=self.parse_performer,
            )

        if next_url := response.css("a.next-page"):
            yield scrapy.http.Request(
                url=next_url.attrib["href"],
                callback=self.parse_performers,
            )

    def parse_performer(self, response):
        performer = Performer(
            source_name=self.result_prefix,
            source_reference=self._id_from_url(response.url),

            name=response.css("h1::text").get().strip(),

            gender=Gender.MALE,

            urls=[
                Link(
                    site=LinkSite.STUDIO,
                    quality=LinkQuality.SOURCE,
                    url=response.url,
                )
            ]
        )

        yield performer
