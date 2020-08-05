# -*- coding: utf-8 -*-

import logging
from urllib.parse import quote_plus
import re
import json

import scrapy

from .nike_ca_helpers import find_data
from .nike_ca_helpers import extract_val_re

from .c_nike_ca_results_page import parse_results_page

logger = logging.getLogger("")


def parse_main(response):
    """
    First build a list of links of api calls for all of the pages of results.
    """

    try:
        json_string = find_data(response)
    except ValueError as ve:
        logger.error(ve)
    else:
        # print(json_string)
        data = json.loads(json_string)

        # with open("nike.json", 'w', encoding='utf-8') as nike:
        #     nike.writelines(json_string)

        next_page = extract_val_re(data, "pageData")
        assert len(next_page) == 1, "could not extract api URL"

        pageData = next_page[0]

        list_of_page_urls = generate_api_calls(pageData)  # an api call per page

        # just use a single page for testing
        list_of_page_urls = [list_of_page_urls[0]]
        for page_url in list_of_page_urls:
            yield scrapy.Request(page_url,
                                 parse_results_page)


# construct api call urls
def generate_api_calls(pageData):
    """
    Uses the 'next' and 'totalResources' fields of pageData
    Generate a list of fully formed URLS that together will get all of the products in the current search
    """
    list_of_urls = []

    base_url = "https://api.nike.com/cic/browse/v1?queryid=products&endpoint="
    next = pageData['next']  # non url encoded uri for api
    totalResources = pageData['totalResources']

    # use default number of items per page
    items_per_page = int(re.search("count=([0-9]*)", next).group(1))

    # Do not change number of items per page from the default 24 because the response
    # seems to be missing items between item number 24 and 25.
    # items_per_page = 48
    # next = re.sub("count=[0-9]*", f"count={items_per_page}", next)

    last_page_num = int(totalResources/items_per_page)

    for i in range(0, 1+last_page_num):
        uri = re.sub("anchor=[0-9]*", f"anchor={i*items_per_page}", next)
        encoded_uri = quote_plus(uri)

        full_url = base_url + encoded_uri
        list_of_urls.append(full_url)

    return list_of_urls
