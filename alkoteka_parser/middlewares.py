import random
from scrapy import signals
from itemadapter import is_item, ItemAdapter
from alkoteka_parser.settings import USER_AGENT_LIST, CUSTOM_COOKIES

class AlkotekaParserSpiderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        return None

    def process_spider_output(self, response, result, spider):
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        pass

    def process_start_requests(self, start_requests, spider):
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

class AlkotekaParserDownloaderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        return None

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

class ProxyMiddleware:
    def process_request(self, request, spider):
        proxy_list = []
        if proxy_list:
            proxy = random.choice(proxy_list)
            request.meta['proxy'] = proxy
            spider.logger.info(f'Using proxy: {proxy}')


class CustomCookiesMiddleware:
    def process_request(self, request, spider):
        request.cookies.update(CUSTOM_COOKIES)


class RandomUserAgentMiddleware:
    def __init__(self, user_agents):
        self.user_agents = user_agents

    @classmethod
    def from_crawler(cls, crawler):
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        ]
        return cls(user_agents)

    def process_request(self, request, spider):
        if self.user_agents and 'User-Agent' not in request.headers:
            request.headers['User-Agent'] = random.choice(self.user_agents)

class RandomProxyMiddleware:
    def __init__(self, proxies):
        self.proxies = proxies

    @classmethod
    def from_crawler(cls, crawler):
        proxies = [
        ]
        return cls(proxies)

    def process_request(self, request, spider):
        if self.proxies and 'proxy' not in request.meta:
            proxy = random.choice(self.proxies)
            request.meta['proxy'] = proxy