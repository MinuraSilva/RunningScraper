import json
import logging

import scrapy

logger = logging.getLogger("adidas_ca")


def parse_availability(response, **cb_kwargs):
    availability_kwargs = {}

    raw_text = response.css("::text").get()
    availability_json = json.loads(raw_text)
    aj = availability_json  # shorter alias

    availability_kwargs["availability_status"] = aj["availability_status"]

    list_of_available_sizes = []  # used for ES search. Also used as keys for dict_of_stock/dict_of_sku
    dict_of_stock = {}
    dict_of_sku = {}

    for variation in aj["variation_list"]:
        size = variation["size"]
        stock = variation["availability"]
        sku = variation["sku"]
        availability_status = variation["availability_status"]  # not needed currently

        if stock > 0:
            list_of_available_sizes.append(size)

        dict_of_stock[size] = stock
        dict_of_sku[size] = sku

    availability_kwargs["available_sizes"] = list_of_available_sizes
    availability_kwargs["stock"] = json.dumps(dict_of_stock)
    availability_kwargs["sku"] = json.dumps(dict_of_sku)

    print(list_of_available_sizes)
    print(dict_of_stock)
    print(dict_of_sku)

    cb_kwargs["availability_page"] = availability_kwargs
    yield cb_kwargs
