import scrapy

# for handling errback / errors
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

import logging
import re

import json


def parse_availability(response, **kwargs):
    cb_kwargs = kwargs

    raw_text = response.css("::text").get()
    availability_json = json.loads(raw_text)
    aj = availability_json  # shorter alias

    general_availability = aj["availability_status"]

    if general_availability == "IN_STOCK":
        list_of_available_sizes = []  # used for ES search. Also used as keys for dict_of_stock/dict_of_sku
        dict_of_stock = {}
        dict_of_sku = {}

        for variation in aj["variation_list"]:
            size = variation["size"]
            stock = variation["availability"]
            sku = variation["sku"]
            availability_status = variation["availability_status"]  # not needed currently

            list_of_available_sizes.append(size)
            dict_of_stock[size] = stock
            dict_of_sku[size] = sku
        print(list_of_available_sizes)
        print(dict_of_stock)
        print(dict_of_sku)

    else:
        pass  # none available; discard

    yield {}