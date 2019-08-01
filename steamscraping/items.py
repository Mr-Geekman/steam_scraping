# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import re
from typing import Union
from datetime import datetime

import scrapy
from scrapy.loader.processors import MapCompose, Compose, TakeFirst, Identity

from steamscraping.settings import REVIEWS_TO_PASS, DAYS_EARLIER


class StrToInt:
    def __init__(self, default=None):
        self.defautl = default

    def __call__(self, int_str: str):
        """
        Получить из строки число, если возможно, иначе None
        :param int_str: значение для преобраз
        :return: int или None
        """
        try:
            return int(int_str)
        except ValueError:
            return self.defautl


class StrToDate:
    def __init__(self):
        pass

    def __call__(self, date_str):
        """
        Получить представление даты в виде datetime по ее строковому представлению
        :param date_str: строка с датой
        :return: datetime, если возможно, иначе исходную строку
        """
        datetime_formats = ('%d %b, %Y', '%b %Y', '%B %Y', '%B, %Y', '%Y')
        for datetime_format in datetime_formats:
            try:
                return datetime.strptime(date_str, datetime_format)
            except ValueError:
                pass
        # TODO: добавить логгирование, чтобы все подобные случаи фиксить
        print("-------------{}------------".format(date_str))
        return date_str


class GameNumReviews:
    """
    Вспомогательные методы для процессинга количества рецензий
    """
    @staticmethod
    def filter_by_num_review(num_reviews: int) -> Union[int, None]:
        """
        Отфильтруем игры, у которых недостаточно рецензий
        :param num_reviews: число рецензий
        :return: число рецензий, если их достаточно, иначе None
        """
        if num_reviews >= REVIEWS_TO_PASS:
            return num_reviews
        else:
            return None


class GameReleaseDate:
    """
    Вспомогательные методы для процессинга даты релиза игры
    """
    @staticmethod
    def filter_by_date(date):
        """
        Отфильтруем игры, у которых слишком старый срок выхода
        :date num_reviews: дата
        :return: число рецензий, если их достаточно, иначе None
        """
        if (isinstance(date, datetime) and
                (datetime.now() - date).days > DAYS_EARLIER):
            return None
        else:
            return date


class GameDescription:
    """
    Вспомогательные методы для процессинга описаний
    """
    @staticmethod
    def remove_divs(value):
        left_border = value.find('>')
        right_border = value.rfind('<')
        return value[left_border + 1, right_border]


class Game(scrapy.Item):
    """
    Модель игры для парсинга
    """
    game_id = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field(
        output_processor=Compose(
            GameDescription.remove_divs,
            lambda x: x.strip()
        )
    )
    num_reviews = scrapy.Field(
        input_processor=Compose(
            MapCompose(
                lambda x: re.match(r'\((.*?)\)', x).group(0),
                TakeFirst(),
                StrToInt(0)
            ),
            max
        ),
        output_processor=GameNumReviews.filter_by_num_review
    )
    release_date = scrapy.Field(
        input_processor=Compose(
            TakeFirst(),
            StrToDate()
        ),
        output_processor=GameReleaseDate.filter_by_date
    )
    specs = scrapy.Field(
        input_processor=Identity()
    )
    tags = scrapy.Field(
        input_processor=Compose(
            Identity,
            lambda x: x.strip()
        )
    )
    price = scrapy.Field(
        input_processor=Compose(
            TakeFirst(),
            StrToInt(0)
        )
    )

    # developer
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