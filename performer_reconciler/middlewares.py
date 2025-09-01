from datetime import datetime
import json
import pathlib
import time
import typing
from urllib.parse import urlparse

from scrapy.responsetypes import responsetypes
from scrapy.exceptions import IgnoreRequest
from warcio.archiveiterator import ArchiveIterator
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


class CommonCrawlIndexedPage(typing.TypedDict):
    url: str
    mime: str
    status: str
    digest: str
    length: str
    offset: str
    filename: str
    timestamp: str


class CommonCrawlMiddleware:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()

        collinfo_path = self._collinfo_file_location()

        if not collinfo_path.exists():
            collinfo_path.parent.mkdir(parents=True, exist_ok=True)

            collinfo = self.scraper.get(
                url="https://index.commoncrawl.org/collinfo.json",
            ).json()

            with collinfo_path.open("w") as f:
                json.dump(collinfo, f)

        with self._collinfo_file_location().open("r") as f:
            self.COLLECTION_INDEXES = json.load(f)

    def _collinfo_file_location(self):
        return pathlib.Path("/tmp/httpcache/commoncrawl/collinfo.json")

    def _collection_index_dir(self, collection_id: str):
        return pathlib.Path(f"/tmp/httpcache/commoncrawl/{collection_id}")

    def _find_url_in_collection(self, url: str, collection_id: str) -> typing.Optional[CommonCrawlIndexedPage]:
        collection_dir = self._collection_index_dir(collection_id)

        if not collection_dir.exists():
            collection_dir.mkdir(parents=True, exist_ok=True)

        domain = urlparse(url).netloc.replace("www.", "")
        domain_file = collection_dir / f"{domain}.json"

        if not domain_file.exists():
            domain_index_url = f"https://index.commoncrawl.org/{collection_id}-index?url={domain}/*&output=json"

            print(f"Fetching Common Crawl index for domain {domain} from {domain_index_url}")
            time.sleep(15)

            response = self.scraper.get(
                url=domain_index_url,
            )

            with domain_file.open("w") as f:
                entries = []
                for line in response.iter_lines(decode_unicode=True):
                    entry = json.loads(line)
                    entries.append(entry)
                json.dump(entries, f)

        request_path = urlparse(url).path.rstrip("/")

        with domain_file.open("r") as f:
            domain_data = json.load(f)

            for entry in domain_data:
                if "message" in entry:
                    continue

                entry_path = urlparse(entry["url"]).path.rstrip("/")

                if entry_path == request_path:
                    return entry

    def _find_url_in_indexes(self, url: str, oldest_date: typing.Optional[datetime]) -> typing.Optional[CommonCrawlIndexedPage]:
        for index_data in self.COLLECTION_INDEXES:
            index_end = datetime.fromisoformat(index_data["to"])

            if oldest_date and index_end < oldest_date:
                continue

            if data := self._find_url_in_collection(url, index_data["id"]):
                if data["status"] in ["400", "403", "404", "410", "429", "500", "502", "503", "504"]:
                    print(f"Found URL in Common Crawl but status is {data['status']}")
                    continue

                return data

        return None

    def process_request(self, request, spider):
        cc_record = self._find_url_in_indexes(request.url, oldest_date=request.meta.get("oldest_date"))

        if not cc_record:
            raise IgnoreRequest(f"URL not found in Common Crawl: {request.url}")

        cc_url = f'https://data.commoncrawl.org/{cc_record["filename"]}'

        offset, length = int(cc_record['offset']), int(cc_record['length'])
        byte_range = f'bytes={offset}-{offset+length-1}'

        response = self.scraper.get(
            url=cc_url,
            headers={
                **request.headers.to_unicode_dict(),
                "Range": byte_range,
            },
            stream=True,
        )

        if response.status_code != 206:
            raise IgnoreRequest(f"Common Crawl did not return a valid location: {request.url}")

        response_headers = {}

        stream = ArchiveIterator(response.raw)
        for warc_record in stream:
            if warc_record.rec_type == 'response':
                response_header_data = warc_record.http_headers
                response_headers = dict(response_header_data.headers)
                response_content = warc_record.content_stream().read()

        if not response_headers:
            raise IgnoreRequest(f"Common Crawl did not return headers: {request.url}")

        respcls = responsetypes.from_args(
            headers=response_headers,
            url=cc_record["url"],
            body=response_content,
        )

        return respcls(
            url=cc_record["url"],
            headers=response_headers,
            status=response_header_data.get_statuscode(),
            body=response_content,
            request=request,
        )
