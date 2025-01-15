from dataclasses import dataclass, field
from typing import Optional
import enum
import scrapy


class BreastType(enum.Enum):
    AUGMENTED = enum.auto()
    NATURAL = enum.auto()


class Ethnicity(str, enum.Enum):
    ASIAN = "ASIAN"
    BLACK = "BLACK"
    CAUCASIAN = "CAUCASIAN"
    INDIAN = "INDIAN"
    LATIN = "LATIN"
    MIDDLE_EASTERN = "MIDDLE_EASTERN"
    MIXED = "MIXED"
    OTHER = "OTHER"


class EyeColor(str, enum.Enum):
    BLACK = "BLACK"
    BLUE = "BLUE"
    BROWN = "BROWN"
    GREEN = "GREEN"
    GREY = "GREY"
    HAZEL = "HAZEL"
    RED = "RED"


class Gender(str, enum.Enum):
    FEMALE = "FEMALE"
    INTERSEX = "INTERSEX"
    MALE = "MALE"
    NON_BINARY = "NON_BINARY"
    TRANSGENDER_FEMALE = "TRANSGENDER_FEMALE"
    TRANSGENDER_MALE = "TRANSGENDER_MALE"


class HairColor(str, enum.Enum):
    AUBURN = "AUBURN"
    BALD = "BALD"
    BLACK = "BLACK"
    BLONDE = "BLONDE"
    BRUNETTE = "BRUNETTE"
    GREY = "GREY"
    RED = "RED"
    VARIOUS = "VARIOUS"
    WHITE = "WHITE"


@dataclass
class BodyModification:
    location: str
    description: Optional[str]


@dataclass
class Performer:
    source_reference: str
    source_name: str

    name: str
    gender: Gender

    disambiguation: Optional[str] = ""
    aliases: list[str] = field(default_factory=list)

    birth_date: Optional[str] = ""
    death_date: Optional[str] = ""

    ethnicity: Optional[Ethnicity] = None
    country: Optional[str] = None

    eye_color: Optional[EyeColor] = None
    hair_color: Optional[HairColor] = None

    height: Optional[int] = 0
    weight: Optional[int] = 0

    breast_type: Optional[BreastType] = None
    cup_size: Optional[str] = ""
    band_size: Optional[int] = 0
    hip_size: Optional[int] = 0
    waist_size: Optional[int] = 0

    career_start_year: Optional[int] = 0
    career_end_year: Optional[int] = 0

    tattoos: list[BodyModification] = field(default_factory=list)
    piercings: list[BodyModification] = field(default_factory=list)

    urls: list[str] = field(default_factory=list)

    image_url: Optional[str] = ""


@dataclass
class SourceReference:
    source_reference: str
    source_name: str


@dataclass
class Scene:
    source_reference: str
    source_name: str

    title: str
    details: str

    studio: SourceReference

    urls: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    performers: list[SourceReference] = field(default_factory=list)

    studio_code: Optional[str] = ""
    duration: Optional[int] = 0
    director: Optional[str] = ""

    release_date: Optional[str] = ""
    production_date: Optional[str] = ""

    cover_image_url: Optional[str] = ""


@dataclass
class Studio:
    source_reference: str
    source_name: str

    name: str
    urls: list[str]

