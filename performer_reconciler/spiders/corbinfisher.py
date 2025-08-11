from .libertymedia import LibertyMediaSpider


class CorbinFisherSpider(LibertyMediaSpider):
    name = "corbinfisher"
    result_prefix = "corbinfisher"
    allowed_domains = ["corbinfisher.com"]

    trailer_prefix = "https://corbinfisher.com/tour"
    model_prefix = "https://corbinfisher.com/tour/models"
    scene_categories = [
        "Collaborations",
        "guys",
    ]


class CorbinFisherSelectSpider(LibertyMediaSpider):
    name = "corbinfisher-select"
    result_prefix = "corbinfisher-select"
    allowed_domains = ["corbinfisher.com"]

    trailer_prefix = "https://corbinfisher.com/select"
    model_prefix = "https://corbinfisher.com/select/models"
    scene_categories = [
        "select",
    ]


class HotCollegeFucksSpider(LibertyMediaSpider):
    name = "corbinfisher-hcf"
    result_prefix = "corbinfisher-hcf"
    allowed_domains = ["www.hotcollegefucks.com"]

    trailer_prefix = "https://www.hotcollegefucks.com/tour"
    model_prefix = "https://www.hotcollegefucks.com/tour/models"
    scene_categories = [
        "movies",
    ]


class BiCollegeFucksSpider(LibertyMediaSpider):
    name = "corbinfisher-bcf"
    result_prefix = "corbinfisher-bcf"
    allowed_domains = ["www.bicollegefucks.com"]

    trailer_prefix = "https://www.bicollegefucks.com/tour"
    model_prefix = "https://www.bicollegefucks.com/tour/models"
    scene_categories = [
        "movies",
    ]
