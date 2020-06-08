# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from datetime import datetime
from elasticsearch import Elasticsearch

# class SportsScraperPipeline:
#     def process_item(self, item, spider):
#         return item


class ElasticsearchPipeline:

    index_name = 'adidas_ca_items'  # the index name for indexing regular product items

    def __init__(self, es_uri, es_port):
        self.es_uri = es_uri
        self.es_port = es_port

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            es_uri=crawler.settings.get('ES_URI'),
            es_port=crawler.settings.get('ES_PORT'),
        )

    def open_spider(self, spider):
        self.es = Elasticsearch([{"host": self.es_uri,
                                  "port": self.es_port}])

    def close_spider(self, spider):
        self.es.transport.close()

    def process_item(self, item, spider):
        self.es.index(index=self.index_name, body=item)
        return item
