BOT_NAME = 'alkoteka_parser'

SPIDER_MODULES = ['alkoteka_parser.spiders']
NEWSPIDER_MODULE = 'alkoteka_parser.spiders'

ROBOTSTXT_OBEY = False
DOWNLOAD_DELAY = 1
COOKIES_ENABLED = True

CUSTOM_COOKIES = {
    'region_id': '23',
    'city_id': '23',
    'region_meta': 'krasnodar',
    'city_meta': 'krasnodar',
}

USER_AGENT_LIST = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
]


USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
}

ITEM_PIPELINES = {
    'alkoteka_parser.pipelines.AlkotekaParserPipeline': 300,
}

LOG_LEVEL = 'DEBUG'