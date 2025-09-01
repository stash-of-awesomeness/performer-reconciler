from urllib.parse import urljoin
from datetime import datetime
import scrapy

from performer_reconciler.items import EyeColor, Gender, HairColor, Link, LinkQuality, LinkSite, Performer, Scene, SourceReference
from performer_reconciler.spiders.commoncrawl import CommonCrawlSpider


class HelixStudiosCCSpider(CommonCrawlSpider):
    name = "helixstudios_cc"
    result_prefix = "helixstudios-cc"
    allowed_domains = ["helixstudios.com"]

    async def start(self):
        yield scrapy.http.Request(
            url="https://www.helixstudios.com/videos/",
            callback=self.parse_videos,
        )

        yield scrapy.http.Request(
            url="https://www.helixstudios.com/models/",
            callback=self.parse_performers,
        )

    def parse_videos(self, response):
        for video in response.css(".grid-item-wrapper > a"):
            if release_date := video.css(".date::text").get():
                release_date = release_date.strip()
                release_date = datetime.strptime(release_date, "%B %d, %Y")

            yield scrapy.http.Request(
                url=urljoin(response.url, video.attrib["href"]),
                callback=self.parse_video,
                meta={"oldest_date": release_date},
            )

        if next_link := response.css(".pagination a.next"):
            yield scrapy.http.Request(
                url=urljoin(response.url, next_link.attrib["href"]),
                callback=self.parse_videos,
            )

    def parse_video(self, response):
        scene_id = response.url.rsplit("/", 2)[1]

        if scene_date := response.xpath('//div[@class="info-items"]/span[@class="info-item date"]/text()').get():
            try:
                scene_date = scene_date.replace("rd", "").replace("th", "").replace("st", "").replace("nd", "")
                scene_date = datetime.strptime(scene_date.strip(), "%B %d, %Y").date()
            except ValueError:
                scene_date = None

        if scene_image := response.css("video").attrib.get("poster"):
            scene_image = scene_image.replace("img/960w/", "").replace(".jpg", "_1920.jpg")
            scene_code = scene_image.rsplit("/", 1)[1].rsplit("_", 1)[0]
        else:
            scene_image = ""
            scene_code = ""

        if scene_details := response.xpath('//div[contains(@class, "description-content")]/p'):
            scene_details = ["".join(details.xpath(".//text()").getall()).strip() for details in scene_details]
            scene_details = "\n\n".join(scene_details).strip()
        else:
            scene_details = ""

        if scene_director := response.css(".director::text").get():
            scene_director = scene_director.strip()

        scene = Scene(
            source_name=self.result_prefix,
            source_reference=scene_id,

            studio=SourceReference(
                source_name=self.result_prefix,
                source_reference=response.css(".studio-name::text").get(),
            ),

            title=response.xpath('//div[@class="video-info"]/span[1]/text()').get(),
            details=scene_details,

            studio_code=scene_code,
            director=scene_director,

            release_date=scene_date,
            cover_image_url=scene_image,

            urls=[
                Link(
                    site=LinkSite.STUDIO,
                    quality=LinkQuality.SOURCE,
                    url=response.url.split("?")[0],
                ),
                Link(
                    site=LinkSite.STUDIO,
                    quality=LinkQuality.NON_CANONICAL,
                    url=response.url.rsplit("/", 1)[0] + "/",
                ),
            ],
        )

        scene_performers = response.css(".video-cast a.thumbnail-link")
        for performer in scene_performers:
            performer_id = performer.attrib["href"].rsplit("/", 2)[1]
            scene.performers.append(
                SourceReference(
                    source_name=self.result_prefix,
                    source_reference=performer_id,
                )
            )

            yield scrapy.http.Request(
                url=urljoin(response.url, performer.attrib["href"]),
                callback=self.parse_performer,
            )

        yield scene

    def parse_performers(self, response):
        for performer in response.css(".browse-results-grid a.thumbnail-link"):
            yield scrapy.http.Request(
                url=urljoin(response.url, performer.attrib["href"]),
                callback=self.parse_performer,
            )

        if next_link := response.css(".pagination a.next"):
            yield scrapy.http.Request(
                url=urljoin(response.url, next_link.attrib["href"]),
                callback=self.parse_performers,
            )

    def parse_performer(self, response):
        EYE_MAP = {
            "": None,
            "Black": EyeColor.BLACK,
            "Blue": EyeColor.BLUE,
            "Brown": EyeColor.BROWN,
            "Green": EyeColor.GREEN,
            "Hazel": EyeColor.HAZEL,
            "Other": None,
        }

        HAIR_MAP = {
            "": None,
            "Black": HairColor.BLACK,
            "Blond": HairColor.BLONDE,
            "Brown": HairColor.BRUNETTE,
            "Red": HairColor.RED,
            "Sandy": HairColor.BLONDE,
        }

        if height := response.xpath('//span[text()="Height"]/following-sibling::text()').get():
            height = height.strip()

        if weight := response.xpath('//span[text()="Weight"]/following-sibling::text()').get():
            weight = weight.strip()

        if hair_color := response.xpath('//span[text()="Hair"]/following-sibling::text()').get():
            hair_color = HAIR_MAP[hair_color.strip()]

        if eye_color := response.xpath('//span[text()="Eyes"]/following-sibling::text()').get():
            eye_color = EYE_MAP[eye_color.strip()]

        performer_image = response.css(".model-headshot-image-wrapper img").attrib.get("src")

        performer = Performer(
            source_name=self.result_prefix,
            source_reference=response.url.rsplit("/", 2)[1],

            name=response.css(".model-bio > h1::text").get().strip(),

            gender=Gender.MALE,

            height=height,
            weight=weight,

            hair_color=hair_color,
            eye_color=eye_color,

            image_url=performer_image,

            urls=[
                Link(
                    site=LinkSite.STUDIO,
                    quality=LinkQuality.SOURCE,
                    url=response.url.split("?")[0],
                ),
            ]
        )

        yield performer

        for scene in response.css(".model-latest-content a.thumbnail-link"):
            yield scrapy.http.Request(
                url=urljoin(response.url, scene.attrib["href"]),
                callback=self.parse_video,
            )

        for scene in response.css(".model-videos a.thumbnail-link"):
            yield scrapy.http.Request(
                url=urljoin(response.url, scene.attrib["href"]),
                callback=self.parse_video,
            )

        for partner in response.css(".scene-partners a.thumbnail-link"):
            yield scrapy.http.Request(
                url=urljoin(response.url, partner.attrib["href"]),
                callback=self.parse_performer,
            )
