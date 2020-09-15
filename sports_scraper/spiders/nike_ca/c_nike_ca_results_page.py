# -*- coding: utf-8 -*-

import logging
from urllib.parse import quote_plus
import re
import json
import scrapy

from .nike_ca_helpers import find_data, extract_val_re, build_item_page_url
from .d_nike_ca_item_page import parse_item_page

logger = logging.getLogger("")


def parse_results_page(response):
    data = json.loads(response.text)

    # Note: only extracting the url for the main item and not other variation ("pdpUrl") since the html on a single
    # item's page contains all of the information for all of the variations.
    products = extract_val_re(data, ["products", "products", "url"])

    for item in products:
        item_url = build_item_page_url(item)
        yield scrapy.Request(item_url,
                             parse_item_page)
