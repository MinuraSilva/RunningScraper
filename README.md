# RunningScraper

## How to Run Scraper
`scrapy crawl adidas_ca -o quotes.json`<br>
- adidas_ca is the name assigned to the scraper. Remember to set the start URLs (in `sports_scraper/spiders/adidas_ca/adidas_ca.py`) before running.
- By default this will dump the data to a json file. To enable indexing into a ElasticSearch database, first make sure ElasticSearch is runnning and then enable `ITEM_PIPELINES` in `sports_scraper/settings.py`.

Notes:<br>
[Scrapy debugging notes](https://github.com/MinuraSilva/RunningScraper/blob/master/other/scrapy_commands.py)<br>
[Scraping websites notes](https://github.com/MinuraSilva/RunningScraper/blob/master/scrapy-scraping-notes..md)
