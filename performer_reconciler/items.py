from dataclasses import dataclass, field
from typing import Optional
import enum
import scrapy


class BreastType(str, enum.Enum):
    AUGMENTED = "AUGMENTED"
    NATURAL = "NATURAL"


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


class LinkQuality(str, enum.Enum):
    SOURCE = "SOURCE"
    CURATED = "CURATED"
    AGGREGATED = "AGGREGATED"
    NON_CANONICAL = "NON_CANONICAL"
    USER_EDITED = "USER_EDITED"
    UNKNOWN = "UNKNOWN"


class LinkSite(str, enum.Enum):
    # Curated databases
    ADULT_DVD_TALK = "ADULT_DVD_TALK"
    AFDB = "AFDB"
    ASHEMALE_TUBE = "ASHEMALE_TUBE"
    BGAFD = "BGAFD"
    COCK_SUCKERS_GUIDE = "COCK_SUCKERS_GUIDE"
    DATA18 = "DATA18"
    DB_NAKED = "DB_NAKED"
    DEFINE_FETISH = "DEFINE_FETISH"
    EGAFD = "EGAFD"
    EURO_BABE_INDEX = "EURO_BABE_INDEX"
    EURO_PORN_STAR = "EURO_PORN_STAR"
    GEVI = "GEVI"
    IAFD = "IAFD"
    IMDB = "IMDB"
    INDEXXX = "INDEXXX"
    PORN_TEEN_GIRL = "PORN_TEEN_GIRL"
    SHEMALE_MODEL_DATABASE = "SHEMALE_MODEL_DATABASE"
    THE_BEST_PORN = "THE_BEST_PORN"
    THENUDE = "THENUDE"
    TMDB = "TMDB"
    TPDB = "TPDB"
    WAYBIG = "WAYBIG"

    # Curated JAV databases
    GRAVURE_FIT = "GRAVURE_FIT"
    GVDB = "GVDB"
    IDOL_EROTIC = "IDOL_EROTIC"
    MINNANO_AV = "MINNANO_AV"
    MSIN = "MSIN"
    R18_DEV = "R18_DEV"
    SOUGOU_WIKI = "SOUGOU_WIKI"
    WAP_DB = "WAP_DB"
    XCITY = "XCITY"
    XS_LIST = "XS_LIST"

    # User-edited wikis
    AV_WIKI = "AV_WIKI"
    BABEPEDIA = "BABEPEDIA"
    BOOBPEDIA = "BOOBPEDIA"
    FREEONES = "FREEONES"
    PORNOPEDIA = "PORNOPEDIA"
    WIKIDATA = "WIKIDATA"
    WIKIFEET_X = "WIKIFEET_X"
    WIKIPEDIA = "WIKIPEDIA"
    WIKIPORNO = "WIKIPORNO"

    # Gallery distributors
    BABE_SOURCE = "BABE_SOURCE"
    BABES_AND_STARS = "BABES_AND_STARS"
    PIC_HUNTER = "PIC_HUNTER"
    PORN_PICS = "PORN_PICS"

    # Social media
    BLUE_SKY = "BLUE_SKY"
    FACEBOOK = "FACEBOOK"
    FET_LIFE = "FET_LIFE"
    INSTAGRAM = "INSTAGRAM"
    KICK = "KICK"  # Kick Streaming
    MYSPACE = "MYSPACE"
    REDDIT = "REDDIT" # Reddit User
    SNAPCHAT = "SNAPCHAT"
    THREADS = "THREADS"
    TIKTOK = "TIKTOK"
    TWITCH = "TWITCH"
    TWITTER = "TWITTER"
    YOUTUBE = "YOUTUBE"

    # Link aggregators
    ALLMYLINKS = "ALLMYLINKS"
    BEACONS = "BEACONS"
    HOOBE = "HOOBE"
    LINKTREE = "LINKTREE"
    LNK_BIO = "LNK_BIO"
    MILKSHAKE = "MILKSHAKE"
    SNIPFEED = "SNIPFEED"

    # JAV distributors
    DMM_FANZA = "DMM_FANZA"
    MGSTAGE = "MGSTAGE"

    # Amateur scene distributors (elligible)
    AP_CLIPS = "AP_CLIPS"
    CLIPS_4_SALE = "CLIPS_4_SALE"
    I_WANT_CLIPS = "I_WANT_CLIPS"
    LOYAL_FANS = "LOYAL_FANS"
    MANYVIDS = "MANYVIDS"
    MFC_SHARE = "MFC_SHARE"
    MY_DIRTY_HOBBY = "MY_DIRTY_HOBBY"
    PORNHUB = "PORNHUB"
    UVIU = "UVIU"
    XVIDEOS = "XVIDEOS"

    # Amateur scene distributors (not elligible)
    CAM4 = "CAM4"
    CAMSODA = "CAMSODA"
    CHATURBATE = "CHATURBATE"
    FANCENTRO = "FANCENTRO"
    FANSLY = "FANSLY"
    FANTIA = "FANTIA"
    ONLYFANS = "ONLYFANS"
    JUSTFORFANS = "JUSTFORFANS"
    MY_FREE_CAMS = "MY_FREE_CAMS"
    MYM = "MYM"
    PATREON = "PATREON"
    PEACH = "PEACH"
    STRIPCHAT = "STRIPCHAT"

    # Modelling agencies
    MODEL_MAYHEM = "MODEL_MAYHEM"
    MODEL_AGENCY = "MODEL_AGENCY"

    # Stash-Box Instances
    STASH_DB = "STASH_DB"
    FANS_DB = "FANS_DB"
    PMV_STASH = "PMV_STASH"

    # Generic
    HOME_PAGE = "HOME_PAGE" # Home / Official Website
    STUDIO = "STUDIO" # Studio / Studio Profile
    UNKNOWN = "UNKNOWN"


@dataclass
class Link:
    quality: LinkQuality
    site: LinkSite
    url: str


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

    urls: list[Link] = field(default_factory=list)

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

    urls: list[Link] = field(default_factory=list)
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
    urls: list[Link]

