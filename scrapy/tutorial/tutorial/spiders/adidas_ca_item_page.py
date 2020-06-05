import scrapy

# for handling errback / errors

import logging
import re

import tutorial.spiders.adidas_ca_availability as adidas_ca_availability

from .adidas_ca_helpers import extract_item_code, append_selectors, headers


def parse_item_page(response, **kwargs):
    cb_kwargs = kwargs
    sidebar = response.css("div[class*='sidebar-wrapper']")

    sale_price = sidebar.css("span[class*='price__value--sale']::text").get()
    cb_kwargs["sale_price"] = get_price(sale_price)

    original_price = sidebar.css("span[class*='price__value--crossed']::text").get()
    cb_kwargs["original_price"] = get_price(original_price)

    try:
        cb_kwargs["sale_percentage"] = \
            (cb_kwargs["original_price"] - cb_kwargs["sale_price"]) / cb_kwargs["original_price"]
    except:
        cb_kwargs["sale_percentage"] = 0

    cb_kwargs["colour"] = sidebar.css("h5[class*='color']::text").get()

    rating_selector = sidebar.css("button[data-auto-id*=rating-review]")
    parse_rating = get_rating(rating_selector)
    cb_kwargs["num_rating"] = parse_rating['num_ratings']
    cb_kwargs["rating"] = parse_rating['rating']

    item_key = extract_item_code(response.url)
    cb_kwargs["item_key"] = item_key
    availability_url = f'https://www.adidas.ca/api/products/tf/{item_key}/availability?sitePath=en'
    cb_kwargs["availability_url"] = availability_url
    cb_kwargs["category_tags"] = get_category_tags(response.css("div[class*='pre-header']"))
    # remember to search both category_tags and brand_sub_category for tags.
    img_url = response.css("link[id='pdp-hero-image']::attr(href)").get()
    cb_kwargs["img_url"] = img_url.replace("images/h_320", "images/h_600")  # increase size of img to 600px

    # before indexing, check to be sure that this is a product page (sometimes there are incorrect links to wrong
    # pages). Also check that item stock != 0 and item sale_price < original price.
    # If all of these conditions are not met, skip indexing and raise error.

    request = scrapy.Request(availability_url,
                             callback=adidas_ca_availability.parse_availability,
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