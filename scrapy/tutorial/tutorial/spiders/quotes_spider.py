import scrapy

# for handling errback / errors
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

import logging


class QuotesSpider(scrapy.Spider):
    name = "quotes"

    # This can also be done globally for all scrapers in the settings.py file.
    # This only applies to the global logger for this scraper's activity. Better to add a handler as below to still
    # allow the messages to be printed to the console as well.
    # custom_settings = {"LOG_FILE": "logger.txt",
    #                    "LOG_LEVEL": "WARNING"}

    # Copy WARN and above logs to a file (in addition to console
    elevated_file_handler = logging.FileHandler("log.txt")
    elevated_file_handler.setLevel("WARN")  # logs all elevated (at or above WARN level)

    # create formatter
    formatter = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s')
    elevated_file_handler.setFormatter(formatter)

    # There are multiple diffenent loggers used in scrapy, only a few of the error messages are sent to this crawlers
    # logger, so instead add the file handler to the base logger.
    # my_logger = logging.getLogger(name)
    # my_logger.addHandler(elevated_file_handler)

    base_logger = logging.getLogger("")
    base_logger.addHandler(elevated_file_handler)


# if not using start_requests() method. Callback must be named 'parse'
    # start_urls = [
    #     'http://quotes.toscrape.com/page/1/',
    #     'http://quotes.toscrape.com/page/2/',
    # ]

    def start_requests(self):
        urls = [
            'http://quotes.toscrape.com/page/1/',
            'http://quotes.toscrape.com/nonexistent'
        ]
        for url in urls:
            yield scrapy.Request(url=url,
                                 callback=self.parse,
                                 errback=self.errback) # remov errback if not using errorback

    def parse(self, response):
        # If you want to write to disk directly (also uncomment code below
        # page = response.url.split("/")[-2]
        # filename = 'quotes-%s.html' % page

        quotes = response.css('div.quote')
        for q in quotes:
            text = q.css('span.text::text').get()
            author = q.css('span small.author::text').get()
            tags = q.css('div.tags a.tag::text').getall()
            summary = {"text": text, "author": author, "tags": str(tags)}

            yield summary

        next_page = response.css("li.next a::attr(href)").get()  # be careful if using .css("li.next a").attrib['href']
        # syntax as this doesn't return None if tag does not exist

        # add a single url to scrape
        if next_page is not None:
            # print("****************************")
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, self.parse)

            # Or use just this line which does relative url join automatically:
            # yield response.follow(next_page, callback=self.parse)

        # add multiple urls to scrape (note that follow_all can take a selector and automatically extract the 'href'
        # attribute value instead of taking an actual url):
        # anchors = response.css('ul.pager a')
        # yield from response.follow_all(anchors, callback=self.parse)
        # See bottom of this page for more info https://doc.scrapy.org/en/latest/intro/tutorial.html#intro-tutorial

        # If you want to save directly to a file and not to output too console which can then be written to a disk using
        # the '-o' flag:
        # with open(filename, 'wb') as f:
        #     f.write(response.body)
        # self.log('Saved file %s' % filename)

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
