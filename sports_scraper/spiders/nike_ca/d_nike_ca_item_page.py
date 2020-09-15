# -*- coding: utf-8 -*-

import json
import logging
from datetime import datetime


from .nike_ca_helpers import find_data, extract_val_re

logger = logging.getLogger("")


def parse_item_page(response):
    """
    May output more than one item if there are multiple variations on sale (data for all variations appear on html of
    any of its variations)
    """
    data = json.loads(find_data(response))

    variations = extract_val_re(data, ["Threads", "products"])[0]

    main_var_id = get_main_item_id()


    main_parse_kwargs = {
        "scrape_time": str(datetime.now()),
        "domain": "www.nike.com/ca",
        "brand": "nike",

    }
    pass


def get_main_item_id(variations_dict):

    for v in variations_dict.keys():
        if str(variations_dict[v]["mainColor"]) == str(True):
            return v