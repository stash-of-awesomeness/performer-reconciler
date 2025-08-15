from performer_reconciler.items import (
    Link, LinkQuality, LinkSite, Performer, Scene, Studio, SourceReference,
    Ethnicity, EyeColor, Gender, HairColor,
)
from datetime import datetime
import scrapy
import string


class TheNudeSpider(scrapy.Spider):
    name = "thenude"
    result_prefix = "thenude"
    allowed_domains = ["www.thenude.com"]

    def start_requests(self):
        for letter in string.ascii_lowercase:
            yield scrapy.http.Request(
                url=f"https://www.thenude.com/model_index_{letter}.html?page=1",
                callback=self.parse_models,
            )

        for letter in string.ascii_lowercase + string.digits:
            yield scrapy.http.Request(
                url=f"https://www.thenude.com/index.php?page=cover_index&letter={letter}",
                callback=self.parse_sites,
            )

    def _normalize_model_url(self, model_url):
        model_id = model_url.rsplit("_", 1)[1].split(".")[0]

        return f"https://www.thenude.com/_{model_id}.htm"

    def parse_models(self, response):
        model_links = response.css("#model_index a[rel=popover]")

        for model in model_links:
            yield scrapy.http.Request(
                url=self._normalize_model_url(model.attrib["href"]),
                callback=self.parse_model,
            )

        next_link = response.css("a[title='Next page']")
        
        if next_link:
            next_link = next_link.attrib["href"]

            yield scrapy.http.Request(
                url=next_link,
                callback=self.parse_models,
            )

    def parse_model(self, response):
        ETHNICITY_MAP = {
            "Arab": Ethnicity.MIDDLE_EASTERN,
            "Asian": Ethnicity.ASIAN,
            "Caucasian": Ethnicity.CAUCASIAN,
            "Ebony": Ethnicity.BLACK,
            "Indian": Ethnicity.INDIAN,
            "Latina": Ethnicity.LATIN,
            "Mixed": Ethnicity.MIXED,
        }

        HAIR_MAP = {
            "Black": HairColor.BLACK,
            "Blond": HairColor.BLONDE,
            "Brown": HairColor.BRUNETTE,
            "Fair": None,
            "Red": HairColor.RED,
        }

        model_id = response.url.rsplit("_", 1)[1].split(".")[0]

        bio_list = response.css(".bio-list")

        hair_color = None
        if hair_color := bio_list.css("li:contains('Hair Colour')::text").get():
            hair_color = hair_color.strip()

            if hair_color:
                hair_color = HAIR_MAP[hair_color]

        ethnicity = None
        if ethnicity := bio_list.css("li:contains(Ethnicity)::text").get():
            ethnicity = ETHNICITY_MAP[ethnicity]

        country = None
        if country := bio_list.css("li:contains(Birthplace)::text").get():
            country = country.strip()

        height = None
        if height := bio_list.css("li:contains('Height:')::text").get():
            height = height.split(" ", 1)[0].strip()

            if height in ["???", ""]:
                height = 0
            else:
                height = int(height)

        birth_date = ""
        if birth_date := bio_list.css("li:contains('Born:')::text").get():
            birth_date = birth_date.strip()
            if birth_date:
                try:
                    birth_date = datetime.strptime("1 " + birth_date, "%d %B %Y").date()
                    birth_date = birth_date.isoformat().rsplit("-", 1)[0]
                except ValueError:
                    birth_date = ""

        career_start_year = 0
        if career_start_year := bio_list.css("li:contains('First Seen')::text").get():
            try:
                career_start_year = int(career_start_year.strip())
            except ValueError:
                career_start_year = 0

        career_end_year = 0
        if career_end_year := bio_list.css("li:contains('Last Seen')::text").get():
            try:
                career_end_year = int(career_end_year.strip())
            except ValueError:
                career_end_year = 0

        links = []
        for link in response.css(".model-model-links .tnap_out_link"):
            links.append(
                Link(
                    site=LinkSite.UNKNOWN,
                    quality=LinkQuality.AGGREGATED,
                    url=link.attrib["href"],
                )
            )

        yield Performer(
            source_reference=model_id,
            source_name="thenude",

            name=response.css("h1 > .model-name::text").get(),
            gender=Gender.FEMALE,

            birth_date=birth_date,

            country=country,
            ethnicity=ethnicity,

            height=height,

            hair_color=hair_color,

            career_start_year=career_start_year,
            career_end_year=career_end_year,

            urls=[
                Link(
                    site=LinkSite.THENUDE,
                    quality=LinkQuality.SOURCE,
                    url=response.url,
                ),
                *links,
            ],
        )

    def parse_sites(self, response):
        site_links = response.css(".three-col-list.list-group > li > a")

        for site in site_links:
            yield scrapy.http.Request(
                url=site.attrib["href"],
                callback=self.parse_site,
            )

    def parse_site(self, response):
        breadcrumbs = response.css(".breadcrumbs-left > a")
        site_link = breadcrumbs[2]

        site_id = site_link.attrib["href"].rsplit("/", 2)[1]
        site_name = site_link.css("::text").get().replace("Videos & Photosets", "").strip()

        links = []
        for link in response.css(".reviews > div > p:contains('Reviewed by') > a"):
            links.append(
                Link(
                    site=LinkSite.UNKNOWN,
                    quality=LinkQuality.AGGREGATED,
                    url=link.attrib["href"],
                )
            )

        yield Studio(
            source_reference=site_id,
            source_name="thenude",

            name=site_name,
            urls=[
                Link(
                    site=LinkSite.THENUDE,
                    quality=LinkQuality.SOURCE,
                    url=site_link.attrib["href"],
                ),
                *links,
            ],
        )
