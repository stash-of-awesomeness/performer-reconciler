from performer_reconciler.items import (
    Performer, Scene, SourceReference, Studio,
    Ethnicity, EyeColor, Gender, HairColor,
)
from datetime import datetime
from urllib.parse import urljoin
import scrapy


class IafdSpider(scrapy.Spider):
    name = "iafd"
    allowed_domains = ["www.iafd.com"]

    def __init__(self, performer_id=None, studio_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.performer_id = performer_id
        self.studio_id = studio_id

        if self.performer_id is not None:
            self.result_prefix = f"iafd-{self.performer_id}"

            self.custom_settings = {
                "DEPTH_LIMIT": 3,
            }

        elif self.studio_id is not None:
            self.result_prefix = f"iafd-{self.studio_id}"

            self.custom_settings = {
                "DEPTH_LIMIT": 3,
            }
        else:
            self.result_prefix = "iafd"

    def start_requests(self):
        if self.performer_id is not None:
            yield scrapy.http.Request(
                url=f"https://www.iafd.com/person.rme/id={self.performer_id}",
                callback=self.parse_performer,
            )
        elif self.studio_id is not None:
            yield scrapy.http.Request(
                url=f"https://www.iafd.com/studio.rme/studio={self.studio_id}",
                callback=self.parse_studio,
            )
        else:
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

    def parse_studio(self, response):
        studio_id = response.url.rsplit("=", 1)[1].rstrip("/")
        studio_name = response.css("title::text").get().split(" - studio lookup - ")[0].strip()

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

    def parse_title(self, response):
        scene_title = response.css("h1::text").get().rsplit(" (", 1)[0]
        studio_link = response.css(".bioheading:contains('Studio') + .biodata > a")

        studio_id = studio_link.attrib["href"].rsplit("/", 2)[1].split("=")[1]

        scene_date = response.css(".bioheading:contains('Release Date') + .biodata::text").get()

        if scene_date:
            scene_date = scene_date.strip()

            if "\n" in scene_date:
                scene_date, _ = scene_date.split("\n", 1)
                scene_date = scene_date.strip()

            if " (" in scene_date:
                scene_date, _ = scene_date.split(" (", 1)

            if scene_date != "No Data":
                scene_date = datetime.strptime(scene_date, "%b %d, %Y").date()
            else:
                scene_date = ""
        else:
            scene_date = ""

        scene_details = response.css("#synopsis .padded-panel::text").get()

        if not scene_details:
            scene_details = ""

        performers = []

        yield Scene(
            source_reference=response.url.split("=")[1],
            source_name="iafd",

            title=scene_title,
            details=scene_details,

            release_date=scene_date,

            studio=SourceReference(
                source_reference=studio_id,
                source_name="iafd",
            ),
            performers=performers,
 
            urls=[
                response.url,
            ],
        )

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

        yield scrapy.http.Request(
            url=f"https://www.iafd.com/studio.rme/studio={studio_id}",
            callback=self.parse_studio,
        )

    def parse_performer(self, response):
        GENDER_MAP = {
            "Man": Gender.MALE,
            "Trans man": Gender.TRANSGENDER_MALE,
            "Trans woman": Gender.TRANSGENDER_FEMALE,
            "Woman": Gender.FEMALE,
        }

        ETHNICITY_MAP = {
            "Asian": Ethnicity.ASIAN,
            "Black": Ethnicity.BLACK,
            "Caucasian": Ethnicity.CAUCASIAN,
            "Ethnic": Ethnicity.OTHER,
            "Eurasian": Ethnicity.OTHER,
            "Indian": Ethnicity.INDIAN,
            "Latin": Ethnicity.LATIN,
            "Mediteranean": Ethnicity.OTHER,
            "Middle Eastern": Ethnicity.MIDDLE_EASTERN,
            "Multi-ethnic": Ethnicity.MIXED,
            "Native American": Ethnicity.OTHER,
            "North African": Ethnicity.BLACK,
            "No data": None,
            "Romani": Ethnicity.OTHER,
            "Polynesian": Ethnicity.OTHER,
            "South Asian": Ethnicity.ASIAN,
            "Unknown": None,
        }

        HAIR_MAP = {
            "Auburn": HairColor.AUBURN,
            "Bald": HairColor.BALD,
            "Black": HairColor.BLACK,
            "Bleached": HairColor.BLONDE,
            "Blond": HairColor.BLONDE,
            "Blue": HairColor.VARIOUS,
            "Brown": HairColor.BRUNETTE,
            "Brown Wig": HairColor.BRUNETTE,
            "Dark Blond": HairColor.BLONDE,
            "Dark Brown": HairColor.BRUNETTE,
            "Dirty Blond": HairColor.BLONDE,
            "Dyed": HairColor.VARIOUS,
            "Green": HairColor.VARIOUS,
            "Grey": HairColor.GREY,
            "Honey Blond": HairColor.BLONDE,
            "Light Brown": HairColor.BRUNETTE,
            "Magenta": HairColor.VARIOUS,
            "No data": None,
            "Pink": HairColor.VARIOUS,
            "Purple": HairColor.VARIOUS,
            "Red": HairColor.RED,
            "Sandy Blond": HairColor.BLONDE,
            "Salt and Pepper": HairColor.GREY,
            "Shaved": HairColor.BALD,
            "Strawberry Blond": HairColor.BLONDE,
            "Unknown": None,
            "Various": HairColor.VARIOUS,
            "Various Wigs": HairColor.VARIOUS,
            "White": HairColor.WHITE,
        }

        EYE_MAP = {
            "Blue": EyeColor.BLUE,
            "Brown": EyeColor.BROWN,
            "Dark Brown": EyeColor.BROWN,
            "Gray": EyeColor.GREY,
            "Green": EyeColor.GREEN,
            "Hazel": EyeColor.HAZEL,
            "LightBrown": EyeColor.BROWN,
            "Red": None,
            "Unknown": None,
        }

        NATIONALITY_MAP = {
            "African American": "United States",
            "Albanian": "Albania",
            "Algerian": "Algeria",
            "American": "United States",
            "Andorran": "Andorra",
            "Angolan": "Angola",
            "Arabic": None,
            "Argentinian": "Argentina",
            "Armenian": "Armenia",
            "Australian": "Australia",
            "Austrian": "Austria",
            "Bahamian": "Bahamas",
            "Barbadian": "Barbados",
            "Belarusian": "Belarus",
            "Belarussian": "Belarus",
            "Belgian": "Belgium",
            "Belizean": "Belize",
            "Beninese": "Benin",
            "Bolivian": "Bolivia",
            "Bosnian": "Bosnia",
            "Brazilian": "Brazil",
            "British": "UK",
            "Bulgarian": "Bulgaria",
            "Cambodian": "Cambodia",
            "Canadian": "Canada",
            "Cape Verdean": "Cape Verde",
            "Caribbean": None,
            "Cherokee": "United States",
            "Chilean": "Chile",
            "Chinese": "China",
            "Colombian": "Colombia",
            "Congolese": "Democratic Republic of the Congo",
            "Costa Rican": "Costa Rica",
            "Creole": None,
            "Croatian": "Croatia",
            "Cuban": "Cuba",
            "Czech": "Czechia",
            "Danish": "Denmark",
            "Dominican": "Dominican Republic",
            "Dutch": "Netherlands",
            "East-Indian": "India",
            "Ecuadorian": "Ecuador",
            "Egyptian": "Egypt",
            "English": "UK",
            "Eritrean": "Eritrea",
            "Estonian": "Estonia",
            "Ethiopean": "Ethiopea",
            "Eurasian": None,
            "Filipino": "Phillipines",
            "Finnish": "Finland",
            "French": "France",
            "French Canadian": "Canada",
            "Georgian": "Georgia",
            "German": "Germany",
            "Ghanaian": "Ghana",
            "Greek": "Greece",
            "Guamanian": "Guam",
            "Guatemalan": "Guatemala",
            "Guinean": "Guinea",
            "Hawaiian": "United States",
            "Honduran": "Honduras",
            "Hungarian": "Hungary",
            "Icelandic": "Iceland",
            "Indian": "India",
            "Indonesian": "Indonesia",
            "Irish": "Ireland",
            "Israeli": "Israel",
            "Italian": "Italy",
            "Jamaican": "Jamaica",
            "Japanese": "Japan",
            "Jewish": None,
            "Kazakh": "Kazakhstan",
            "Kazakhstani": "Kazakhstan",
            "Kenyan": "Kenya",
            "Korean": "South Korean",
            "Kyrgyz": "Kyrgyzstan",
            "Laotian": "Laos",
            "Latvian": "Latvia",
            "Lebanese": "Lebanon",
            "liSwati": None,
            "Lithuanian": "Lithuania",
            "Luxembourger": "Luxembourg",
            "Macedonian": "Macedonia",
            "Malagasy": "Madagascar",
            "Malaysian": "Malaysia",
            "Maltese": "Malta",
            "Mexican": "Mexico",
            "Moldavian": "Moldovo",
            "Mongolian": "Mongolia",
            "Moroccan": "Morocco",
            "Native American": "United States",
            "Navaho": "United States",
            "New Zealander": "New Zealand",
            "Nicaraguan": "Nicaragua",
            "Nigerian": "Nigeria",
            "North African": None,
            "Norwegian": "Norway",
            "No data": None,
            "Pakistani": "Pakistan",
            "Palestinian": "Palestine",
            "Panamanian": "Panama",
            "Paraguayan": "Paraguay",
            "Persian": None,
            "Peruvian": "Peru",
            "Polish": "Poland",
            "Polynesian": None,
            "Portuguese": "Portugal",
            "Puerto Rican": "Puerto Rico",
            "Romani": None,
            "Romanian": "Romania",
            "Russian": "Russia",
            "Rwandan": "Rwanda",
            "Salvadorean": "El Salvadore",
            "Samoan": "Samoa",
            "Scottish": "UK",
            "Senegalese": "Senegal",
            "Serbian": "Serbia",
            "Sicilian": "Italy",
            "Singaporean": "Singapore",
            "Slovak": "Slovakia",
            "Slovenian": "Slovenia",
            "South African": "South Africa",
            "Spanish": "Spain",
            "Surinamese": "Surinam",
            "Swedish": "Sweden",
            "Swiss": "Switzerland",
            "Syrian": "Syria",
            "Taiwanese": "Taiwan",
            "Thai": "Thailand",
            "Togan": None,
            "Togolese": "Togo",
            "Trinidadian": "Trinidad and Tobago",
            "Tunisian": "Tunisia",
            "Turkish": "Turkey",
            "Ugandan": "Uganda",
            "Ukrainian": "Ukraine",
            "Unknown": None,
            "Uruguayan": "Uruguay",
            "Uzbek": "Uzbekistan",
            "Venezuelan": "Venezuela",
            "Vietnamese": "Vietnam",
            "Welsh": "UK",
            "Yugoslavian": "Yugoslavia",
        }

        performer_image = response.css("#headshot img").attrib["src"]
        if "nophoto" in performer_image:
            performer_image = ""

        performer_websites = response.css("a[target=starlet][href]")
        links = [website.attrib["href"] for website in performer_websites]

        ethnicity = response.css(".bioheading:contains(Ethnicity) + .biodata::text").get()
        if "/" in ethnicity:
            ethnicity = Ethnicity.MIXED
        else:
            ethnicity = ETHNICITY_MAP[ethnicity]

        hair_color = HAIR_MAP[response.css(".bioheading:contains(Hair) + .biodata::text").get().split("/")[0]]
        eye_color = EYE_MAP[response.css(".bioheading:contains(Eye) + .biodata::text").get().strip()]
        country = NATIONALITY_MAP[response.css(".bioheading:contains(Nationality) + .biodata::text").get().split(",")[0]]

        height = response.css(".bioheading:contains(Height) + .biodata::text").get()
        if height and "(" in height:
            height = height.split("(", 1)[1]
            height = height.split(" ")[0]
            height = int(height)
        else:
            height = 0

        weight = response.css(".bioheading:contains(Weight) + .biodata::text").get()
        if weight and "(" in weight:
            weight = weight.split("(", 1)[1]
            weight = weight.split(" ")[0]
            weight = weight.split(".")[0]
            weight = int(weight)
        else:
            weight = 0

        measurements = response.css(".bioheading:contains(Measurements) + .biodata::text").get()
        cup_size = ""
        band_size = 0
        hip_size = 0
        waist_size = 0

        if measurements and "-" in measurements:
            bra, hip_size, waist_size = measurements.split("-")

            if hip_size == "??":
                hip_size = 0
            else:
                hip_size = int(hip_size)

            if waist_size == "??":
                waist_size = 0
            else:
                waist_size = int(waist_size)

        yield Performer(
            source_reference=response.url.rsplit("=", 1)[1],
            source_name="iafd",

            name=response.css("h1::text").get().strip(),
            gender=GENDER_MAP[response.css(".bioheading:contains(Gender) + .biodata::text").get()],

            ethnicity=ethnicity,
            hair_color=hair_color,
            eye_color=eye_color,
            country=country,

            height=height,
            weight=weight,

            cup_size=cup_size,
            band_size=band_size,
            hip_size=hip_size,
            waist_size=waist_size,

            image_url=performer_image,

            urls=[
                response.url,
                *links,
            ],
        )

