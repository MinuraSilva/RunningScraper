# interactive mode
# scrapy shell "http://quotes.toscrape.com"  # must use double quotes

# Running (Note: -o appends output if file already exists)
## Single scrapy script - Run from location of script
scrapy runspider quotes_spider.py -o quotes.json


## Scrapy project - run from root of project.
# The name is the name defined in the 'name' variable in any of the spider files in projectname/projectname/spiders/<spidername>.py
scrapy crawl quotes -o quotes.json


# Filter by custom attributes (other than class):
response.css('span[attr_name="attr_val"]::text').get()()  // optionally have no tag name and just have attr e.g. response.css('[attr_name="attr_val"]::text')

# Get attribute value:
## Method 1
Link = Link1.css('span.title a::attr(href)').get()[0]

## Method 2 - simpler if only a single 
Link = Link1.css('span.title').attrib['href']

# Wildcards in attribute value. e.g. the class attribute whose valuse includes "menu" anywhere in the value. Can also use ^ or $ instead of * to select
# values which start or end with the value. Note: Even though the symbol appears nect to the attribute name, it applies to the attribute value.
selector = response.css('div[class*="menu"]')

# Select the nth child in the css selector. Note: the space before the colon is mandatory. Also be sure to not go over the max.
# If you go over the max number, and the parent selector (div.product_card) is not unique, this will automatically keep searching for the first
# div.product that has atleast n children and return that. 
selector = response.css('div.product_card :nth-child(2)')



# To pass values that are extracted from a previous page:
# https://doc.scrapy.org/en/latest/topics/request-response.html#topics-request-response-ref-request-callback-arguments

# Command line arguments for a crawler (e.g. pass in url)
# https://doc.scrapy.org/en/latest/topics/spiders.html#spiderargs

# headers for adidas.ca
wget -O- https://www.adidas.ca/
--header="Host: www.adidas.ca"
--header="User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0"
--header="Accept-Language: en-US,en;q=0.5"
--header="Connection: keep-alive"
# formatted for scrapy:
{"Host": "www.adidas.ca", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0", "Accept-Language": "en-US,en;q=0.5", "Connection": "keep-alive",}

# Add header when using shel:
$ scrapy shell
>>> from scrapy import Request
>>> req = Request('yoururl.com', headers={"header1":"value1"})
>>> fetch(req)
>>> response.css('...')

