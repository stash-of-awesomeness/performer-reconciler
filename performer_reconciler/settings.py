import pathlib

BOT_NAME = "performer_reconciler"

SPIDER_MODULES = ["performer_reconciler.spiders"]
NEWSPIDER_MODULE = "performer_reconciler.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "PerformerReconciler/requests"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 1
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "performer_reconciler.middlewares.PerformerReconcilerSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    "performer_reconciler.middlewares.CloudScraperMiddleware": 950,
    "scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware": None,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    "performer_reconciler.pipelines.PerformerReconcilerPipeline": 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 30 * 24 * 60 * 60
HTTPCACHE_DIR = "/tmp/httpcache"
HTTPCACHE_IGNORE_HTTP_CODES = [
    400, 401, 403, 404,
    # Rate limiting
    429,
    500, 502, 503, 504,
    # Cloudflare-specific codes
    520, 521, 522, 523, 524, 525, 526,
]
HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

location_base = (pathlib.Path(__file__) / ".." / ".." / "scraped_data").resolve().as_posix()

studio_location = location_base + "/%(result_prefix)s-studios.jsonl.xz"
performer_location = location_base + "/%(result_prefix)s-performers.jsonl.xz"
scene_location = location_base + "/%(result_prefix)s-scenes.jsonl.xz"

feed_settings = {
    "format": "jsonlines",
    "encoding": "utf-8",
    "overwrite": True,
    "postprocessing": [
        "scrapy.extensions.postprocessing.LZMAPlugin",
    ]
}

FEEDS = {
    studio_location: {"item_classes": ["performer_reconciler.items.Studio"], **feed_settings},
    performer_location: {"item_classes": ["performer_reconciler.items.Performer"], **feed_settings},
    scene_location: {"item_classes": ["performer_reconciler.items.Scene"], **feed_settings},
}

try:
    from .local_settings import *
except ImportError:
    pass
