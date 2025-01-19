from performer_reconciler.items import (
    Performer, Scene, Studio, SourceReference,
    Ethnicity, EyeColor, Gender, HairColor,
)

from datetime import date
from urllib.parse import urljoin, urlparse, parse_qs

import scrapy
import string


class GeviSpider(scrapy.Spider):
    name = "gevi"
    allowed_domains = ["gayeroticvideoindex.com"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.result_prefix = "gevi"

    def start_requests(self):
        for first_letter in string.ascii_lowercase:
            for second_letter in string.ascii_lowercase:
                yield scrapy.http.JsonRequest(
                    url=self._url_for_performers(first_letter + second_letter),
                    headers={
                        "Referer": "https://gayeroticvideoindex.com/search",
                    },
                    callback=self.parse_performers,
                )

    def _url_for_performers(self, search, limit=100, offset=0):
        return f"https://gayeroticvideoindex.com/shpr?length={limit}&start={offset}&search%5Bvalue%5D={search}"

    def parse_performers(self, response):
        data = response.json()

        parsed_url = urlparse(response.url)
        parsed_params = parse_qs(parsed_url.query)

        current_page = int(parsed_params["start"][0]) // 100
        last_page = data["recordsFiltered"] // 100

        if current_page < last_page:
            yield scrapy.http.JsonRequest(
                url=self._url_for_performers(parsed_params["search[value]"][0], limit=100, offset=(current_page + 1) * 100),
                callback=self.parse_performers,
            )

        for performer in data["data"]:
            link = scrapy.Selector(text=performer[1]).css("a")

            performer_url = urljoin(response.url, link.attrib["href"])

            yield scrapy.http.Request(
                url=performer_url,
                callback=self.parse_performer,
            )

    def parse_performer(self, response):
        COUNTRY_MAP = {
            "England": "UK",
            "U.K.": "UK",
            "US": "United States",
            "U.S.": "United States",
            "USA": "United States",
        }

        EYE_MAP = {
            "": None,
            "Asian": None,
            "Blue": EyeColor.BLUE,
            "Brown": EyeColor.BROWN,
            "Dark Brown": EyeColor.BROWN,
            "Green": EyeColor.GREEN,
            "Gray": EyeColor.GREY,
            "Grey": EyeColor.GREY,
            "Hazel": EyeColor.HAZEL,
            "Light Blue": EyeColor.BLUE,
            "Light Brown": EyeColor.BROWN,
            "Steel Blue": EyeColor.BLUE,
            "Various": None,
            "Violet": None,
        }

        HAIR_MAP = {
            "": None,
            "Afro": None,
            "Auburn": HairColor.AUBURN,
            "Bald": HairColor.BALD,
            "Balding": HairColor.BALD,
            "Black": HairColor.BLACK,
            "Blond": HairColor.BLONDE,
            "Blue": HairColor.VARIOUS,
            "Braids": None,
            "Brown": HairColor.BRUNETTE,
            "Bushy": None,
            "Curly": None,
            "Dark Blond": HairColor.BLONDE,
            "Dark Brown": HairColor.BRUNETTE,
            "Dark BrownLong": HairColor.BRUNETTE,
            "Dark Red": HairColor.RED,
            "Gray": HairColor.GREY,
            "Graying": HairColor.GREY,
            "Hidden": None,
            "Kinky": None,
            "Lavender": HairColor.VARIOUS,
            "Light": None,
            "Light Blond": HairColor.BLONDE,
            "Light Brown": HairColor.BRUNETTE,
            "Long": None,
            "Long/Short": None,
            "Longish": None,
            "Pink": HairColor.VARIOUS,
            "Platinum": HairColor.BLONDE,
            "Receding": None,
            "Red": HairColor.RED,
            "Salt/Pepper": HairColor.GREY,
            "Shaved": HairColor.BALD,
            "Short": None,
            "Silver": HairColor.GREY,
            "Straight": None,
            "Strawberry": HairColor.AUBURN,
            "Various": HairColor.VARIOUS,
            "Wavy": None,
            "White": HairColor.WHITE,
        }

        ETHNICITY_MAP = {
            "Black": Ethnicity.BLACK,
            "Brown": None,
            "Caramel": None,
            "Deltoids": None,
            "Olive": None,
            "White": Ethnicity.CAUCASIAN,
        }

        data_container = response.css("#data")

        performer_profile_links = data_container.css("div.items-start:contains('See this performer') > a")
        links = []

        for link in performer_profile_links:
            normalized_link = link.attrib["href"]

            if normalized_link:
                links.append(normalized_link)

        performer_attributes = data_container.css(".flex .flex-col > .border .columns-2 .items-start")

        hair_color = None
        if hair_color := performer_attributes.css("div:contains(Hair):not(:contains(Facial)):not(:contains(Body)) + div::text").get():
            hair_color = HAIR_MAP[hair_color.strip()]

        eye_color = None
        if eye_color := performer_attributes.css("div:contains(Eyes) + div::text").get():
            eye_color = EYE_MAP[eye_color.strip().split("/", 1)[0]]

        ethnicity = None
        if skin_color := performer_attributes.css("div:contains(Skin) + div::text").get():
            ethnicity = ETHNICITY_MAP[skin_color.strip()]

        height = None
        if height := performer_attributes.css("div:contains(Height) + div::text").get():
            if "/" in height:
                height = int(height.rsplit("/", 1)[1].rstrip("cm").strip())
            else:
                height = None

        weight = None
        if weight := performer_attributes.css("div:contains(Weight) + div::text").get():
            if "/" in weight:
                weight = int(weight.rsplit("/", 1)[1].rstrip("kg").strip())
            else:
                weight = None

        country = None
        if country := performer_attributes.css("div:contains(From) + div::text").get():
            country = country.strip()

            if "," in country:
                country = country.rsplit(",", 1)[1].strip()
            
            if country in COUNTRY_MAP:
                country = COUNTRY_MAP[country]
            
            if len(country) == 2 and country not in ["UK"]:
                country = "United States"

        performer_id = response.url.split("/")[-1]
        performer_name = data_container.css("h1::text").get().split(" (", 1)[0]

        yield Performer(
            source_reference=performer_id,
            source_name="gevi",

            name=performer_name,
            gender=Gender.MALE,

            ethnicity=ethnicity,
            country=country,

            eye_color=eye_color,
            hair_color=hair_color,

            height=height,
            weight=weight,

            urls=[
                response.url,
                *links,
            ],
        )

        yield scrapy.http.JsonRequest(
            url=self._url_for_performer_episodes(performer_id, performer_name),
            callback=self.parse_episodes,
        )

    def _url_for_performer_episodes(self, performer_id, performer_name, limit=100, offset=0):
        return f"https://gayeroticvideoindex.com/prep?start={offset}&length={limit}&search[value]=&NameKey={performer_id}&PerformerName={performer_name}"

    def parse_episodes(self, response):
        data = response.json()

        parsed_url = urlparse(response.url)
        parsed_params = parse_qs(parsed_url.query)

        performer_id = parsed_params["NameKey"][0]
        performer_name = parsed_params["PerformerName"][0]
        current_page = int(parsed_params["start"][0]) // 100
        last_page = data["recordsFiltered"] // 100

        if current_page < last_page:
            yield scrapy.http.JsonRequest(
                url=self._url_for_performer_episodes(performer_id, performer_name, limit=100, offset=(current_page + 1) * 100),
                callback=self.parse_episodes,
            )

        for scene in data["data"]:
            link = scrapy.Selector(text=scene[2]).css("a")

            scene_url = urljoin(response.url, link.attrib["href"])

            yield scrapy.http.Request(
                url=scene_url,
                callback=self.parse_episode,
            )

    def parse_episode(self, response):
        data_container = response.css("#data > section")

        scene_id = "episode/" + response.url.rsplit("/", 1)[1]

        scene_name = data_container.css("h1::text").get().strip()

        if scene_cover := data_container.css("img[alt][src].hidden"):
            scene_cover = urljoin(urljoin(response.url, "/"), scene_cover.attrib["src"])
        else:
            scene_cover = None

        scene_details = data_container.css("div.text-justify.wideCols-1 > p.mb-2 span::text")

        if scene_details:
            scene_details = "\n\n".join(scene_detail.get().strip() for scene_detail in scene_details)
            scene_details = scene_details.replace("\u2019", "'").replace("\u00a0", " ")
        else:
            scene_details = ""

        performers = []

        scene_credits = data_container.css("div > table > tbody > tr.border-b > td > a")
        for scene_performer in scene_credits:
            performer = SourceReference(
                source_reference=scene_performer.attrib["href"].split("/")[-1],
                source_name="gevi",
            )

            performers.append(performer)

        studio_link = data_container.css(".font-bold > a")
        studio_id = studio_link.attrib["href"].rsplit("/", 1)[1]

        yield Scene(
            source_reference=scene_id,
            source_name="gevi",

            title=scene_name,
            details=scene_details,

            studio=SourceReference(
                source_reference=studio_id,
                source_name="gevi",
            ),
            performers=performers,

            cover_image_url=scene_cover,
            urls=[
                response.url,
            ]
        )
    
    def parse_video(self, response):
        pass
