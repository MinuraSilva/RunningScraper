# RunningScraper

## How to Run Scraper
More info [here](https://github.com/MinuraSilva/RunningScraper/blob/master/other/scrapy_commands.py)

`scrapy crawl adidas_ca -o quotes.json`
adidas_ca is the name assigned to the scraper. Remember to change the start URL to be the last page in Outlet items to avoid scraping too many items during testing.

By default this will dump the data to a json file. To enable indexing into a ElasticSearch database, first make sure ElasticSearch is runnning and enable `ITEM_PIPELINES` in sports_scraper/settings.py
