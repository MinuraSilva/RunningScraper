import scrapy

# for handling errback / errors

import logging
import re

import tutorial.spiders.adidas_ca_availability as adidas_ca_availability

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
    # parsed variations should be passed to a separate ES database for joining at query time

    for item in items:
        cb_kwargs = dict()

        info_card = "div.gl-product-card__details"
        main_item_url = item.css(append_selectors(info_card, "a::attr(href)")).get()
        main_item_url = response.urljoin(main_item_url)
        cb_kwargs["main_item_url"] = main_item_url
        main_item_key = extract_item_code(main_item_url)
        cb_kwargs["main_item_key"] = main_item_key

        cb_kwargs["item_title"] = item.css(append_selectors(info_card, 'span[class$="name"]::text')).get()
        cb_kwargs["item_sub_brand"] = item.css(append_selectors(info_card, 'div[class$="category"]::text')).get()
        cb_kwargs["item_type"] = item.css(append_selectors(info_card, 'div[class$="category"]::attr(title)')).get()
        cb_kwargs["item_num_colours"] = item.css(append_selectors(info_card, 'div[class$="color"]::text')).get()

        cb_kwargs["main_img_url"] = item.css("img:nth-child(1)::attr(src)").get()
        cb_kwargs["source_page"] = response.url

        try:
            cb_kwargs["main_variation"] = parsed_variations['get_main'][main_item_key]
            cb_kwargs["sibling_variations"] = parsed_variations['get_siblings'][main_item_key]
        except:
            # dictionary lookup will fail if there are no variations
            cb_kwargs["main_variation"] = [main_item_key]
            cb_kwargs["sibling_variations"] = [main_item_key]

        for variation in cb_kwargs["sibling_variations"]:
            variation_url = get_variation_url(cb_kwargs["main_item_url"], variation)

            print(variation_url)

            # for colour_variatiton in cb_kwargs["sibling_variations"]
            request = scrapy.Request(variation_url,
                                     callback=parse_item_page,
                                     headers=headers,
                                     cb_kwargs=cb_kwargs)
            # yield cb_kwargs
            yield request

    # todo: uncomment when done; follow next link
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
