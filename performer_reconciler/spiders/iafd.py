from performer_reconciler.items import Performer, Scene, SourceReference, Studio, Gender
from urllib.parse import urljoin
import scrapy


class IafdSpider(scrapy.Spider):
    name = "iafd"
    allowed_domains = ["www.iafd.com"]

    def start_requests(self):
        yield scrapy.http.Request(
            url="https://www.iafd.com/studio.asp",
            callback=self.parse_studio_search,
        )

    def parse_studio_search(self, response):
        studio_select = response.css("select[name=Studio]")
        studio_options = studio_select.css("option")

        for studio_option in studio_options:
            yield scrapy.http.Request(
                url=f"https://www.iafd.com/studio.rme/studio={studio_option.attrib['value']}",
                callback=self.parse_studio,
            )

            return

    def parse_studio(self, response):
        studio_id = response.url.rsplit("=", 1)[1].rstrip("/")
        studio_name = response.css("title::text").get().split(" - studio lookup - ")[0]

        yield Studio(
            source_reference=studio_id,
            source_name="iafd",

            name=studio_name,
            urls=[
                f"https://www.iafd.com/studio.rme/studio={studio_id}",
            ],
        )

        title_rows = response.css("#studio").css("tbody tr")

        for title_row in title_rows:
            title_link = title_row.css("td a")[0]

            yield scrapy.http.Request(
                url=urljoin(response.url, title_link.attrib["href"]),
                callback=self.parse_title,
            )

            return

    def parse_title(self, response):
        scene_title = response.css("h1::text").get().rsplit(" (", 1)[0]
        studio_link = response.css(".bioheading:contains('Studio') + .biodata > a")

        studio_id = studio_link.attrib["href"].rsplit("/", 2)[1].split("=")[1]

        performers = []

        for performer_link in response.css(".castbox a"):
            performers.append(
                SourceReference(
                    source_reference=performer_link.attrib["href"].split("=")[1],
                    source_name="iafd",
                )
            )

            yield scrapy.http.Request(
                url=urljoin(response.url, performer_link.attrib["href"]),
                callback=self.parse_performer,
            )

        yield Scene(
            source_reference=response.url.split("=")[1],
            source_name="iafd",

            title=scene_title,
            details="",

            studio=SourceReference(
                source_reference=studio_id,
                source_name="iafd",
            ),
            performers=performers,
 
            urls=[
                response.url,
            ],
        )

    def parse_performer(self, response):
        GENDER_MAP = {
            "Man": Gender.MALE,
            "Woman": Gender.FEMALE,
        }

        yield Performer(
            source_reference=response.url.rsplit("=", 1)[1],
            source_name="iafd",

            name=response.css("h1::text").get(),
            gender=GENDER_MAP[response.css(".bioheading:contains(Gender) + .biodata::text").get()],

            urls=[
                response.url,
            ],
        )

