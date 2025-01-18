from scrapy.responsetypes import responsetypes
import cloudscraper


class CloudScraperMiddleware:

    def __init__(self):
        self.scraper = cloudscraper.create_scraper()

    def process_request(self, request, spider):
        response = self.scraper.get(request.url, headers=request.headers.to_unicode_dict())

        respcls = responsetypes.from_args(headers=response.headers, url=response.url, body=response.content)

        return respcls(
            url=response.url,
            headers=response.headers,
            status=response.status_code,
            body=response.content,
            request=request,
        )

