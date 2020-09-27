# RunningScrape
A web scraper for extracting data from online stores selling athletic gear (originally intended only for running gear, hence the name) and indexing in an Elasticsearch database with the purpose of finding discounted products.<br>
Currently works for adidas.ca. End goal is to scrape multiple sites including Reebok, Nike, Footlocker and MEC to provide a centralised store of the best deals on athletic gear.

## How to Run Scraper
`scrapy crawl adidas_ca -o quotes.json`<br>
- adidas_ca is the name assigned to the scraper. Remember to set the start URLs (in `sports_scraper/spiders/adidas_ca/adidas_ca.py`) before running.
- By default this will dump the data to a json file. To enable indexing into a ElasticSearch database, first make sure ElasticSearch is runnning and then enable `ITEM_PIPELINES` in `sports_scraper/settings.py`.

Notes:<br>
[Scrapy debugging notes](https://github.com/MinuraSilva/RunningScraper/blob/master/other/scrapy_commands.py)<br>
[Scraping websites notes](https://github.com/MinuraSilva/RunningScraper/blob/master/scrapy-scraping-notes..md)
