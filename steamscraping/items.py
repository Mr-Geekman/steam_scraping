# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import re
from typing import Union, List, Tuple
from datetime import datetime

import scrapy
from scrapy.loader.processors import MapCompose, Compose, TakeFirst, Identity

from steamscraping.settings import REVIEWS_TO_PASS, DAYS_EARLIER, LANGUAGE


# TODO: change message when language selection will be moved to setup.py
class LanguageSelectError(ValueError):
    """
    Language in settings.py is not supported
    """
    def __init__(self):
        message = ("Please select correct language in settings.py: "
                   "russian or english")
        super().__init__(message)


class StrToInt:
    def __init__(self, default=None):
        self.default = default

    def __call__(self, int_str: str):
        """
        Get int from string if it is possible, otherwise default value
        :param int_str: value to convert
        :return: result of converting
        """
        try:
            return int(int_str)
        except ValueError:
            return self.default


class StrToDate:
    def __init__(self):
        if LANGUAGE == 'english':
            self.datetime_formats = (
                '%d %b, %Y', '%b %Y', '%B %Y', '%B, %Y', '%Y'
            )
        elif LANGUAGE == 'russian':
            # TODO: to implement
            pass
        else:
            raise LanguageSelectError()
        pass

    def __call__(self, date_str):
        """
        Get datetime instance from string if it is possible
        :param date_str: string with date
        :return: datetime instance if it is possible (otherwise given string)
        """
        for datetime_format in self.datetime_formats:
            try:
                return datetime.strptime(date_str, datetime_format)
            except ValueError:
                pass
        # TODO: add logging for fixing this cases
        print("-------------{}------------".format(date_str))
        return date_str


class GameNumReviews:
    """
    Service methods for processing num of reviews
    """
    @staticmethod
    def filter_by_num_review(num_reviews: int) -> Union[int, None]:
        """
        Filter games, that have enough reviews
        :param num_reviews: num of reviews
        :return: num of reviews if it is enough, otherwise None
        """
        if num_reviews >= REVIEWS_TO_PASS:
            return num_reviews
        else:
            return None


class GameReleaseDate:
    """
    Service methods for processing game release date
    """
    @staticmethod
    def filter_by_date(release_date):
        """
        Filter games, that have relevant release date (not older than
            in specified in settings)
        :param release_date: release date
        :return: release date if it was filtered, otherwise None
        """
        if (isinstance(release_date, datetime) and
                (datetime.now() - release_date).days > DAYS_EARLIER):
            return None
        else:
            return release_date


class GameDescription:
    """
    Service methods for processing game descriptions
    """
    @staticmethod
    def remove_divs(value):
        """
        Remove div tags around the description
        """
        left_border = value.find('>')
        right_border = value.rfind('<')
        return value[left_border + 1, right_border]


class GameRequirements:
    """
    Class for storing system requirements
    """
    def __init__(self, min_os, min_cpu, min_ram, min_gpu, rec_os, rec_cpu,
                 rec_ram, rec_gpu):
        self.min_os = min_os
        self.min_cpu = min_cpu
        self.min_ram = min_ram
        self.min_gpu = min_gpu
        self.rec_os = rec_os
        self.rec_cpu = rec_cpu
        self.rec_ram = rec_ram
        self.rec_gpu = rec_gpu
        # We can add new useful fields, such as below
        # self.direct_x = direct_x


class GameRequirementsBuilder:
    """
    Class for building object for storing system requirements
    We can pass additional parameters for building
    """
    def __init__(self):
        if LANGUAGE == 'english':
            self.MIN_LABEL = 'Minimum:'
            self.REC_LABEL = 'Recommended:'
            self.OS_LABEL = 'OS:'
            self.CPU_LABEL = 'Processor:'
            self.GPU_LABEL = 'Graphics:'
            self.RAM_LABEL = 'Memory:'
        elif LANGUAGE == 'russian':
            # TODO: to implement
            pass
        else:
            raise LanguageSelectError()

    def __call__(self, data_from_scraper: List[str]) -> GameRequirements:
        """
        Building GameRequirements object
        :param data_from_scraper: data collected by scraper
        :return: GameRequirements instance
        """
        # remove white spaces from collected data
        self._remove_white_spaces(data_from_scraper)

        # split requirements into minimum and recommended requirements
        min_req_list, rec_req_list = self._split_requirements(
            data_from_scraper
        )

        # get operating system
        min_os = self._get_requirement(min_req_list, self.OS_LABEL)
        rec_os = self._get_requirement(rec_req_list, self.OS_LABEL)

        # get processor
        min_cpu = self._get_requirement(min_req_list, self.CPU_LABEL)
        rec_cpu = self._get_requirement(rec_req_list, self.CPU_LABEL)

        # get graphics card
        min_gpu = self._get_requirement(min_req_list, self.GPU_LABEL)
        rec_gpu = self._get_requirement(rec_req_list, self.GPU_LABEL)

        # get ram
        min_ram = self._get_requirement(min_req_list, self.RAM_LABEL)
        rec_ram = self._get_requirement(rec_req_list, self.RAM_LABEL)

        # create GameRequirements object and return it
        return GameRequirements(min_os, min_cpu, min_ram, min_gpu,
                                rec_os, rec_cpu, rec_ram, rec_gpu)

    @staticmethod
    def _remove_white_spaces(data_from_scraper: List[str]) -> None:
        """
        Remove redundant white spaces and elements, that consists only of
            them (\r, \n, \t)
        """
        data_from_scraper = list(map(lambda x: x.strip(), data_from_scraper))
        data_from_scraper.remove('')

    def _split_requirements(
            self, data_from_scraper: List[str]
    ) -> Tuple[List[str], List[str]]:
        """
        Find sublists contains minimum and recommended system requirements
        :param data_from_scraper: scraped data
        :return: two sublists
        """
        min_index_start = 0
        rec_index_start = len(data_from_scraper)
        try:
            min_index_start = data_from_scraper.index(self.MIN_LABEL)
        except ValueError:
            # TODO: add logging for storing errors
            pass
        try:
            rec_index_start = data_from_scraper.index(self.REC_LABEL)
        except ValueError:
            pass
        min_req_list = data_from_scraper[min_index_start: rec_index_start]
        rec_req_list = data_from_scraper[:rec_index_start]
        return min_req_list, rec_req_list

    @staticmethod
    def _get_requirement(
            requirements_list: List[str], label: str
    ) -> Union[str, None]:
        """
        Get from system requirements list the element by label
        :param requirements_list: list with requirements
        :param label: обозначение для требования, которое нужно достать
        :param label: label for requirement to get
        :return: found string or None
        """
        if not requirements_list:
            return None
        try:
            cpu_label_index = requirements_list.index(label)
            return requirements_list[cpu_label_index + 1]
        except (ValueError, IndexError):
            # TODO: to add logging
            return None


class Game(scrapy.Item):
    """
    Model for game
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

    system_requirements = scrapy.Field(
        input_processor=Compose(Identity(), GameRequirementsBuilder())
    )

    # developer = scrapy.Field()
    # pictures = scrapy.Filed()
