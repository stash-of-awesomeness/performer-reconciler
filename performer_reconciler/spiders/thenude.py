from performer_reconciler.items import (
    Performer, Scene, Studio, SourceReference,
    Ethnicity, EyeColor, Gender, HairColor,
)
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
        if height := bio_list.css("li:contains(Height)::text").get():
            height = height.split(" ", 1)[0].strip()

            if height in ["???", ""]:
                height = 0
            else:
                height = int(height)

        yield Performer(
            source_reference=model_id,
            source_name="thenude",

            name=response.css("h1 > .model-name::text").get(),
            gender=Gender.FEMALE,

            country=country,
            ethnicity=ethnicity,

            height=height,

            hair_color=hair_color,

            urls=[
                response.url,
            ],
        )
