import scrapy

# for handling errback / errors

import logging
import re

import tutorial.spiders.adidas_ca_availability as adidas_ca_availability

from .adidas_ca_helpers import extract_item_code, get_price, append_selectors


class AdidasCaSpider(scrapy.Spider):
    name = "adidas_ca"

    # logging
    elevated_file_handler = logging.FileHandler("log.txt")
    elevated_file_handler.setLevel("WARN")  # logs all elevated (at or above WARN level)

    formatter = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s')
    elevated_file_handler.setFormatter(formatter)

    base_logger = logging.getLogger("")
    base_logger.addHandler(elevated_file_handler)

    headers = {
        "Host": "www.adidas.ca",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
    }

    def start_requests(self):
        urls = [
            # 'https://www.adidas.ca/en/men-clothing-outlet',
            'https://www.adidas.ca/en/men-clothing-outlet?start=768'
        ]

        for url in urls:
            yield scrapy.Request(url=url,
                                 callback=self.parse,
                                 headers=self.headers)
                                 # errback=self.errback) # remov errback if not using errorback


    def parse(self, response):
        # if "outlet" not in url name, throw error

        items = response.css("div[data-index]")  # get list of cards on page

        js_code = self.find_str_in_selector_list_text(response.css("script"), re.compile(".*JSON\.parse.*"))
        assert len(js_code) == 1, "Expects exactly one script tag with the colourVariation information"
        js_text = js_code[0].css("::text").get()
        parsed_variations = self.parse_colour_variations(js_text, response.url)
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
                variation_url = self.get_variation_url(cb_kwargs["main_item_url"], variation)

                print(variation_url)

                # for colour_variatiton in cb_kwargs["sibling_variations"]
                request = scrapy.Request(variation_url,
                                         callback=self.parse_item_page,
                                         headers=self.headers,
                                         cb_kwargs=cb_kwargs)
                # yield cb_kwargs
                yield request



        # todo: uncomment when done
        # next_page = response.css("div[class*=pagination__control--next] a::attr(href)").get()
        #
        # if next_page is not None:
        #     next_page = response.urljoin(next_page)
        #     yield scrapy.Request(next_page,
        #                          self.parse,
        #                          headers=self.headers)

    def get_variation_url(self, main_variation_url, variation_key):
        """
        :param main_variation_url: fully formed url for link to the main variation of the item
        :param variation_key: the item_key for the variation
        :return: swaps out the item_key for the main variation with that for the given variation_key
        """

        new_url, num_replacements = re.subn(r'\w{2}\d{4}', variation_key, main_variation_url)
        assert num_replacements==1, f"The number of replacements ({num_replacements}) is not exactly 1."

        return new_url

    def find_str_in_selector_list_text(self, selector_list, regex):
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

    def parse_colour_variations(self, html_js_raw, response_url):
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
            self.logger.error(f"Failed to get colour variations for this url: {response_url}")

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

    def parse_item_page(self, response, **kwargs):
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
        parse_rating = self.get_rating(rating_selector)
        cb_kwargs["num_rating"] = parse_rating['num_ratings']
        cb_kwargs["rating"] = parse_rating['rating']

        item_key = extract_item_code(response.url)
        cb_kwargs["item_key"] = item_key
        availability_url = f'https://www.adidas.ca/api/products/tf/{item_key}/availability?sitePath=en'
        cb_kwargs["availability_url"] = availability_url
        cb_kwargs["category_tags"] = self.get_category_tags(response.css("div[class*='pre-header']"))
        # remember to search both category_tags and brand_sub_category for tags.
        img_url = response.css("link[id='pdp-hero-image']::attr(href)").get()
        cb_kwargs["img_url"] = img_url.replace("images/h_320", "images/h_600")  # increase size of img to 600px


        # before indexing, check to be sure that this is a product page (sometimes there are incorrect links to wrong
        # pages). Also check that item stock != 0 and item sale_price < original price.
        # If all of these conditions are not met, skip indexing and raise error.

        request = scrapy.Request(availability_url,
                                 callback=adidas_ca_availability.parse_availability,
                                 headers=self.headers,
                                 cb_kwargs=cb_kwargs)

        yield request

    def get_rating(self, rating_selector):
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
                actual_score = (star_score-12) / (88-12)
                star_sum += actual_score

            star_sum /= max_stars  # normalize star score

            return {"num_ratings": num_ratings, "rating": star_sum}
        except:
            return {"num_ratings": 0, "rating": float(0)}  # this will be encountered if there are no reviews and therefore no stars

    def get_category_tags(self, pre_header_selector):
        selectors = pre_header_selector.css("li[property='itemListElement'][typeof='ListItem'] span[property='name']")

        category_tags = []
        for category_selector in selectors:
            category_name = category_selector.css("::text").get()
            if category_name.lower() != 'home':
                category_tags.append(category_name.lower())
            else:
                pass  # category names are taken from breadcrumbs list. Ignore 'Home' link.

        return category_tags
