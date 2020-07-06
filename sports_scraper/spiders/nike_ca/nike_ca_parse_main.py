# -*- coding: utf-8 -*-

import copy
import re
import logging
from datetime import datetime
from urllib.parse import urlparse, quote_plus, unquote
import re
import json

import scrapy

from .nike_ca_helpers import extract_val, nike_base64_to_url_encoding

logger = logging.getLogger("")

def parse_main(response):

    try:
        json_string = find_data(response)
    except ValueError as ve:
        logger.error(ve)
    else:
        # print(json_string)
        data = json.loads(json_string)

        # with open("nike.json", 'w', encoding='utf-8') as nike:
        #     nike.writelines(json_string)

        next_page = extract_val(data, "pageData")
        assert len(next_page) == 1, "could not extract api URL"

        pageData = next_page[0]

        generate_api_calls(pageData)

        yield {}


def find_data(response):
    """returns the part of the selector that contains the json as string. Gets everything in between { }"""

    search_script = re.compile("\s*window\.INITIAL_REDUX_STATE")  # start pattern for script containing data

    for a in response.css("script"):
        script = str(a.css("::text").get(default=""))
        if search_script.match(script):
            json_string = re.search("{.*}", script).group()

            return json_string

    raise ValueError("Could not find the script with data in html")


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

    for u in list_of_urls:
        print(u)
        print('\n')

    pass
