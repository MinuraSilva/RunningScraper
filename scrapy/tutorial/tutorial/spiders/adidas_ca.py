import scrapy

# for handling errback / errors

import logging
import re

import tutorial.spiders.adidas_ca_availability as adidas_ca_availability

from .adidas_ca_helpers import extract_item_code, append_selectors, headers
from .adidas_ca_item_page import parse_item_page
from .adidas_ca_parse_main import parse_main

# for handling errback / errors
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

class AdidasCaSpider(scrapy.Spider):
    name = "adidas_ca"

    # logging
    elevated_file_handler = logging.FileHandler("log.txt")
    elevated_file_handler.setLevel("WARN")  # logs all elevated (at or above WARN level)

    formatter = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s')
    elevated_file_handler.setFormatter(formatter)

    base_logger = logging.getLogger("")
    base_logger.addHandler(elevated_file_handler)

    headers = headers

    def start_requests(self):
        urls = [
            # 'https://www.adidas.ca/en/men-clothing-outlet',
            # 'https://www.adidas.ca/en/men-clothing-outlet?start=720'
            'https://www.adidas.ca/en/men-clothing-outlet?start=768'
        ]

        for url in urls:
            yield scrapy.Request(url=url,
                                 callback=parse_main,
                                 headers=self.headers)
                                 # errback=self.errback) # remov errback if not using errorback

    # currently does nothing other than logging
    def errback(self, failure):
        # log all failures
        self.logger.error(repr(failure))

        # in case you want to do something special for some errors,
        # you may need the failure's type:

        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)