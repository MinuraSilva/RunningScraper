import scrapy

# for handling errback / errors
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

import logging

class NikeSpider(scrapy.Spider):
    name = "nike"  # add a country suffix to prevent conflicts when running on other countries

    # logging
    elevated_file_handler = logging.FileHandler("log.txt")
    elevated_file_handler.setLevel("WARN")  # logs all elevated (at or above WARN level)

    formatter = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s')
    elevated_file_handler.setFormatter(formatter)

    base_logger = logging.getLogger("")
    base_logger.addHandler(elevated_file_handler)

    def start_requests(self):
        urls = [
            'https://www.nike.com/ca/w/sale-3yaep',
        ]

        for url in urls:
            yield scrapy.Request(url=url,
                                 callback=self.parse,
                                 errback=self.errback) # remov errback if not using errorback


    def parse(self, response):
        items = response.css("div.product-card__body")  # get list of cards on page

        for item in items:
            cb_kwargs = dict()

            item_url = item.css('a.product-card__link-overlay::attr(href)').get()
            cb_kwargs["item_page_url"] = item_url
            cb_kwargs["source_page"] = response.url  # page where data was scraped from
            cb_kwargs["item_name"] = item.css("div.product-card__title::text").get()
            cb_kwargs["item_category"] = item.css("div.product-card__subtitle::text").get()
            cb_kwargs["num_colours"] = item.css('div[aria-label] span::text').get()
            cb_kwargs["original_price"] = item.css('div[data-test="product-price"]::text').get()
            cb_kwargs["sale_price"] = item.css('div[data-test="product-price-reduced"]::text').get()
            # cb_kwargs["discount_percentage"] = self.calculatePercentage(original_price, sale_price)
            cb_kwargs["image_url"] = item.css('img::attr(src)').get()



            request = scrapy.Request(item_url,
                                     callback=self.parse_item,
                                     cb_kwargs=cb_kwargs)

            # make request to object page

            yield(request)

    def parse_item(self, response, **kwargs):
        kwargs["item_description"] = response.css('div[id="RightRail"] p::text').get()

        # these should be done inside extract_colour_size_availability since there will be multiple colours
        # on the same page
        kwargs["item_colour"] = response.css('div[id="RightRail"] li::text')[0].get()
        kwargs["item_style"] = response.css('div[id="RightRail"] li::text')[1].get()
        kwargs["item_stock"] = -1  # Number of items in stock. If does not exist, set to -1

        yield(kwargs)

        # must availability info for each colou/size combination. Skipping for now.
        def extract_colour_size_availability(response):
            #equivalent mens size =
            #equivalent_womens_size =
            #colour =
            #number_available = # set to -1 if unavailable
            #image_url =
            #model_SKU_code
            #item_type = # shoe, shirt etc
            #gender =
            #other_search_tags =
            #average_review = (out of 5)
            #num_reviews =
            #other_info

            pass


    def get_item_name(self, selector):
        pass

    def get_item_url(self, selector):
        pass

    # currently does nothing other than logging
    def errback(self, failure):
        # log all failures
        self.logger.error(repr(failure))

        # in case you want to do something special for some errors,
        # you may need the failure's type:

        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)