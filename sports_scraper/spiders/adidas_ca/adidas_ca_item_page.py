import re
import logging

import scrapy

from .adidas_ca_helpers import extract_item_code, append_selectors, headers
from .adidas_ca_availability import parse_availability

logger = logging.getLogger("adidas_ca")


def parse_item_page(response, **cb_kwargs):
    item_page_kwargs = {}
    sidebar = response.css("div[class*='sidebar-wrapper']")

    sale_price = sidebar.css("span[class*='price__value--sale']::text").get()
    item_page_kwargs["sale_price"] = get_price(sale_price)

    original_price = sidebar.css("span[class*='price__value--crossed']::text").get()
    if type(original_price)!= str:
        # if the item is not on sale (.get() will return NoneType), the original price has a different tag.
        original_price = sidebar.css("span[class*='price__value']::text").get()

    item_page_kwargs["original_price"] = get_price(original_price)

    if item_page_kwargs["sale_price"] == float(-1):
        item_page_kwargs["on_sale"] = False
    else:
        item_page_kwargs["on_sale"] = True

    item_page_kwargs["sale_percentage"] = get_sale_percentage(item_page_kwargs["original_price"],
                                                              item_page_kwargs["sale_price"])

    item_page_kwargs["absolute_discount"] = get_absolute_discount(item_page_kwargs["original_price"],
                                                              item_page_kwargs["sale_price"])

    item_page_kwargs["colour"] = sidebar.css("h5[class*='color']::text").get()

    rating_selector = sidebar.css("button[data-auto-id*=rating-review]")
    parse_rating = get_rating(rating_selector)
    item_page_kwargs["num_rating"] = parse_rating['num_ratings']
    item_page_kwargs["rating"] = parse_rating['rating']

    item_key = extract_item_code(response.url)
    item_page_kwargs["item_key"] = item_key
    availability_url = f'https://www.adidas.ca/api/products/tf/{item_key}/availability?sitePath=en'
    item_page_kwargs["availability_url"] = availability_url
    item_page_kwargs["category_tags"] = get_category_tags(response.css("div[class*='pre-header']"))
    # remember to search both category_tags and brand_sub_category for tags.
    img_url = response.css("link[id='pdp-hero-image']::attr(href)").get()
    item_page_kwargs["img_url"] = img_url.replace("images/h_320", "images/h_600")  # increase size of img to 600px

    item_page_kwargs["sub_title"] = response.css('div[class^="text-content"] h4::text').get()
    item_page_kwargs["description"] = response.css('div[class^="text-content"] p::text').get()

    # before indexing, check to be sure that this is a product page (sometimes there are incorrect links to wrong
    # pages). Also check that item stock != 0 and item sale_price < original price.
    # If all of these conditions are not met, skip indexing and raise error.

    cb_kwargs["item_page_kwargs"] = item_page_kwargs
    request = scrapy.Request(availability_url,
                             callback=parse_availability,
                             headers=headers,
                             cb_kwargs=cb_kwargs)

    yield request


def get_rating(rating_selector):
    # 5 stars, each star goes from 12-88% If a star is not coloured, it will still be 12%
    try:
        num_ratings = int(rating_selector.css("::text").get())

        ratings = rating_selector.css("div[class*='star-rating'][style*=width]::attr(style)")
        max_stars = 5
        assert len(ratings) == max_stars, "The number of rating stars found is not exactly 5"

        star_sum = float(0)
        for star_selector in ratings:
            star = star_selector.get()
            star_score = float(re.search(r'\d+(\.\d+)?', star).group())
            # The value of each star varies from 12% to 88%, so need to do this to get actual value.
            actual_score = (star_score - 12) / (88 - 12)
            star_sum += actual_score

        star_sum /= max_stars  # normalize star score

        return {"num_ratings": num_ratings, "rating": star_sum}
    except:
        return {"num_ratings": 0,
                "rating": float(0)}  # this will be encountered if there are no reviews and therefore no stars


def get_category_tags(pre_header_selector):
    selectors = pre_header_selector.css("li[property='itemListElement'][typeof='ListItem'] span[property='name']")

    category_tags = []
    for category_selector in selectors:
        category_name = category_selector.css("::text").get()
        if category_name.lower() != 'home':
            category_tags.append(category_name.lower())
        else:
            pass  # category names are taken from breadcrumbs list. Ignore 'Home' link.

    return category_tags


def get_price(price_string):

    if type(price_string) == str:
        return float(re.search(r'\d+(\.\d+)?', price_string).group())
    else:
        return float(-1)  # unable to find price

def get_sale_percentage(original_price, sale_price):
    if ((original_price==float(-1)) or (sale_price==(-1))):
        return 0
    else:
        return (original_price-sale_price)/original_price

def get_absolute_discount(original_price, sale_price):
    if ((original_price==float(-1)) or (sale_price==(-1))):
        return 0
    else:
        return (original_price-sale_price)
