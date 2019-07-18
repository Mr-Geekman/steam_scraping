# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose


class Game(scrapy.Item):
    """
    Модель игры для парсинга
    """
    game_id = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    # num_reviews = scrapy.Field()
    release_date = scrapy.Field()
    # # TODO: to think about output processors
    # tags = scrapy.Field()
    #
    # min_os = scrapy.Field()
    # min_cpu = scrapy.Field()
    # min_ram = scrapy.Field()
    # min_gpu = scrapy.Field()
    #
    # rec_os = scrapy.Field()
    # rec_cpu = scrapy.Field()
    # rec_ram = scrapy.Field()
    # rec_gpu = scrapy.Field()
