import copy
import re
import logging

import scrapy

from .adidas_ca_helpers import extract_item_code, append_selectors, headers
from .adidas_ca_item_page import parse_item_page

logger = logging.getLogger("adidas_ca")


def parse_main(response):

    # if "outlet" not in url name, throw error

    items = response.css("div[data-index]")  # get list of cards on page

    js_code = find_str_in_selector_list_text(response.css("script"), re.compile(".*JSON\.parse.*"))
    assert len(js_code) == 1, "Expects exactly one script tag with the colourVariation information"
    js_text = js_code[0].css("::text").get()
    parsed_variations = parse_colour_variations(js_text, response.url)

    for item in items:
        main_parse_kwargs = dict()

        info_card = "div.gl-product-card__details"
        main_item_url = item.css(append_selectors(info_card, "a::attr(href)")).get()
        main_item_url = response.urljoin(main_item_url)
        main_parse_kwargs["main_item_url"] = main_item_url
        main_item_key = extract_item_code(main_item_url)
        main_parse_kwargs["main_item_key"] = main_item_key

        main_parse_kwargs["item_title"] = item.css(append_selectors(info_card, 'span[class$="name"]::text')).get()
        main_parse_kwargs["item_sub_brand"] = item.css(append_selectors(info_card, 'div[class$="category"]::text')).get()
        main_parse_kwargs["item_type"] = item.css(append_selectors(info_card, 'div[class$="category"]::attr(title)')).get()
        main_parse_kwargs["item_num_colours"] = item.css(append_selectors(info_card, 'div[class$="color"]::text')).get()

        main_parse_kwargs["main_img_url"] = item.css("img:nth-child(1)::attr(src)").get()
        main_parse_kwargs["source_page"] = response.url

        try:
            main_parse_kwargs["main_variation"] = parsed_variations['get_main'][main_item_key]
            main_parse_kwargs["sibling_variations"] = parsed_variations['get_siblings'][main_item_key]
        except:
            # dictionary lookup will fail if there are no variations
            main_parse_kwargs["main_variation"] = [main_item_key]
            main_parse_kwargs["sibling_variations"] = [main_item_key]

        for variation in main_parse_kwargs["sibling_variations"]:

            variation_url = get_variation_url(main_parse_kwargs["main_item_url"], variation)
            main_parse_kwargs["variation_url"] = variation_url

            cb_kwargs = {"main_parse_kwargs": main_parse_kwargs}
            cb_kwargs_deep_cp = copy.deepcopy(cb_kwargs)  # otherwise leads wrong data due to the shallow copy of dict
            # being modified by later iterations of this for loop.

            # for colour_variation in main_parse_kwargs["sibling_variations"]
            request = scrapy.Request(variation_url,
                                     callback=parse_item_page,
                                     headers=headers,
                                     cb_kwargs=cb_kwargs_deep_cp)
            yield request

    # Follow next page
    next_page = response.css("div[class*=pagination__control--next] a::attr(href)").get()

    if next_page is not None:
        next_page = response.urljoin(next_page)
        yield scrapy.Request(next_page,
                             parse_main,
                             headers=headers)


def get_variation_url(main_variation_url, variation_key):
    """
    :param main_variation_url: fully formed url for link to the main variation of the item
    :param variation_key: the item_key for the variation
    :return: swaps out the item_key for the main variation with that for the given variation_key
    """

    new_url, num_replacements = re.subn(r'\w{2}\d{4}', variation_key, main_variation_url)
    assert num_replacements == 1, f"The number of replacements ({num_replacements}) is not exactly 1."

    return new_url


def find_str_in_selector_list_text(selector_list, regex):
    if type(selector_list) == scrapy.selector.unified.Selector:
        selector_list = scrapy.selector.unified.SelectorList([selector_list])
    assert type(selector_list) == scrapy.selector.unified.SelectorList, "Wrong datatype. Must be selector list."

    ret_selectors = []
    for selector in selector_list:
        try:
            if regex.match(selector.css("::text").get()):
                ret_selectors.append(selector)
        except TypeError:  # if selector does not have any text, will cause re to throw exception
            pass

    return scrapy.selector.unified.SelectorList(ret_selectors)


def parse_colour_variations(html_js_raw, response_url):
    """
    html_js_raw in the entire text content of the <script> tag that includes the javascript
    Returns a reverse dictionary that can be used to identify the main variation code given a colour variation
    """
    # todo: The get_main and exhaustive get_siblings dicts are unnecessary.
    # todo: The only necessary data is {main_key: [all sibling_ keys including main, main_keys_2: ...]

    try:
        colour_variation_list = re.findall(r"colorVariations[^\]]*],", html_js_raw)
        colour_variation_list_cleaned = [re.findall(r'\w\w\d+', cv) for cv in colour_variation_list]
        colour_variation_list_cleaned = list(filter(lambda x: len(x) > 0, colour_variation_list_cleaned))
    except:
        colour_variation_list_cleaned = []
        logger.error(f"Failed to get colour variations for this url: {response_url}")

    get_main = {}
    for variations in colour_variation_list_cleaned:
        base_var = variations[0]
        for sub_var in variations:
            get_main[str(sub_var)] = str(base_var)

    get_siblings = {}
    for variations in colour_variation_list_cleaned:
        for sub_var in variations:
            get_siblings[str(sub_var)] = variations

    return {"get_main": get_main, "get_siblings": get_siblings}
