# -*- coding: utf-8 -*-
import logging

import scrapy

from .b_nike_ca_parse_main import parse_main

# for handling errback / errors
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

class NikeCaSpider(scrapy.Spider):

    # todo: problem with logger in all of nike_ca. Also verify adidas_ca loggers work as expected.
    name = 'nike_ca'

    headers = ""

    # logging
    elevated_file_handler = logging.FileHandler("nike_ca.txt")
    elevated_file_handler.setLevel("WARN")  # logs all elevated (at or above WARN level)

    formatter = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s')
    elevated_file_handler.setFormatter(formatter)

    base_logger = logging.getLogger("")
    base_logger.addHandler(elevated_file_handler)

    def start_requests(self):
        urls = [
            'https://www.nike.com/ca/w/sale-3yaep'
        ]

        for url in urls:
            yield scrapy.Request(url=url,
                                 callback=parse_main,
                                 headers=self.headers)
                                 # errback=self.errback) # remov errback if not using errorback