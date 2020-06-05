import scrapy

# for handling errback / errors
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

import logging
import re

import json


def extract_item_code(url):
    code = re.search(r'\w\w\d\d\d\d', url).group()
    return code


def get_price(price_string):

    if type(price_string) == str:
        return float(re.search(r'\d+(\.\d+)?', price_string).group())
    else:
        return float(-1)  # unable to find price


def append_selectors(*args):
    """
    Each argument must be a string.
    Simply appends all of the given arguments with a space in between and returns.
    """

    return_string = ""

    for a in args:
        assert type(a) is str, "append_selectors given non-string argument"
        return_string = return_string + " " + a.strip()

    return_string = return_string.strip()  # remove whitespace after last selector
    return return_string