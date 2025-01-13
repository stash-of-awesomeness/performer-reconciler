from dataclasses import dataclass
from typing import Optional
import enum
import scrapy


class BreastType(enum.StrEnum):
    AUGMENTED = enum.auto()
    NATURAL = enum.auto()


class Ethnicity(enum.StrEnum):
    ASIAN = enum.auto()
    BLACK = enum.auto()
    CAUCASIAN = enum.auto()
    INDIAN = enum.auto()
    LATIN = enum.auto()
    MIDDLE_EASTERN = enum.auto()
    MIXED = enum.auto()
    OTHER = enum.auto()


class EyeColor(enum.StrEnum):
    BLACK = enum.auto()
    BLUE = enum.auto()
    BROWN = enum.auto()
    GREEN = enum.auto()
    GREY = enum.auto()
    HAZEL = enum.auto()
    RED = enum.auto()


class Gender(enum.StrEnum):
    FEMALE = enum.auto()
    INTERSEX = enum.auto()
    MALE = enum.auto()
    NON_BINARY = enum.auto()
    INTERSEX = enum.auto()
    TRANSGENDER_FEMALE = enum.auto()
    TRANSGENDER_MALE = enum.auto()


class HairColor(enum.StrEnum):
    AUBURN = enum.auto()
    BALD = enum.auto()
    BLACK = enum.auto()
    BLONDE = enum.auto()
    BRUNETTE = enum.auto()
    GREY = enum.auto()
    RED = enum.auto()
    VARIOUS = enum.auto()
    WHITE = enum.auto()


@dataclass
class BodyModification:
    location: str
    description: Optional[str]


@dataclass
class Performer:
    reference_id: str
    source_name: str

    name: str
    disambiguation: Optional[str]
    aliases: list[str]

    birth_date: Optional[str]
    death_date: Optional[str]

    ethnicity: Optional[Ethnicity]
    country: Optional[str]

    eye_color: Optional[EyeColor]
    hair_color: Optional[HairColor]

    height: Optional[int]
    gender: Gender

    breast_type: Optional[BreastType]
    cup_size: Optional[str]
    band_size: Optional[int]
    hip_size: Optional[int]
    waist_size: Optional[int]

    career_start_year: Optional[int]
    career_end_year: Optional[int]

    tattoos: list[BodyModification]
    piercings: list[BodyModification]

    urls: list[str]

    image_url: Optional[str]


@dataclass
class Scene:
    reference_id: str
    source_name: str

    title: str
    details: str
    studio_code: Optional[str]
    duration: Optional[int]
    director: Optional[str]

    tags = list[str]

    performers: list[Performer]

    release_date: Optional[str]
    production_date = Optional[str]

    urls = list[str]
    cover_image_url: Optional[str]


@dataclass
class Studio:
    name: str
    urls: list[str]

