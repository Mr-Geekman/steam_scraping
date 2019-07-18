import re
from datetime import datetime

import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst

from steamscraping.items import Game
from steamscraping.settings import DAYS_EARLIER


class GameItemLoader(ItemLoader):
    """
    Кастомный загрузчик с переопределенным output_processor по-умолчанию
    """
    default_output_processor = TakeFirst()


# TODO: see below
# 1) Добавить обработку поля num_reviews - не парсить игру, если обзоров слишком мало
# 2) Очищать поле description от лишнего
# 3) Доставать теги, specs
# 4) Подрубить русский язык при парсинге, если возможно
# 5) Доставать системки и ощищать их
# 6) Реализовать пайплайны для заполнения БД
# 7) Подумать над логгированием
class GameParser(CrawlSpider):
    """
    Класс паука для парсинга новых игр со steam
    """
    name = 'games'
    start_urls = ["https://store.steampowered.com/search/"
                  "?sort_by=Released_DESC&category1=998"]
    allowed_domains = ['steampowered.com']

    rules = (
        Rule(
            LinkExtractor(
                allow='/app/.+',
                restrict_css='#search_result_container'
            ),
            process_request='add_cookies',
            callback='parse_game'
        ),
        Rule(
            LinkExtractor(
                allow='page=(\d+)',
                restrict_css='.search_pagination_right'
            ),
            process_request='add_cookies',
            callback='parse_page'
        )
    )


    def add_cookies(self, request):
        """
        Добавим cookie для обхода ограничений на жестокость и на возраст
        """
        request.cookies.update({'mature_content': '1',
                                'lastagecheckage': '1-0-2000',
                                'birthtime': 943999201})

        return request

    def parse_page(self, response):
        """
        Метод для парсинга страницы с играми, нужен для прекращения парсинга
        в случае прихода ко слишком ранней дате
        :param response: запрос
        """

        # посмотрим на даты релиза игр, которые мы нашли на странице
        # если среди игр на странице есть хоть одна, вышедшая вовремя, то
        # обрабатываем страницу
        release_dates_str = response.css('div.search_released::text').extract()
        for release_date_str in release_dates_str:
            release_date = self._get_release_date(release_date_str)

            if (isinstance(release_date, datetime) and
                    (datetime.now() - release_date).days <= DAYS_EARLIER):
                return self.parse(response)

        pass

    def parse_game(self, response):
        """
        Метод для парсинга самой игры
        :param response: запрос
        """
        # если появляется форма выбора возраста, значит сломались куки
        if '/agecheck/app' in response.url:
            # TODO: добавить логгирование
            print("--------COOKIES BROKEN--------")

        # если формы ввода возраста нет, то все делаем,как обычно
        else:
            loader = GameItemLoader(item=Game(), response=response)

            release_date_str = response.css('div.date ::text').extract_first()
            release_date = self._get_release_date(release_date_str)
            # если дата слишком ранняя - прекращаем обработку игры
            if (isinstance(release_date, datetime) and
                    (datetime.now() - release_date).days > DAYS_EARLIER):
                return
            loader.add_value('release_date', release_date)

            game_id = int(re.match(r'.+/(\d+)/.+', response.url).groups()[0])
            loader.add_value('game_id', game_id)

            loader.add_css('title', '.apphub_AppName ::text')

            # TODO: to clean it up
            loader.add_css('description', '#game_area_description')

            # # TODO: select num_reviews
            #
            # # get system requirements
            # info_block = response.css('div[data-os="win"] div').extract()
            # # TODO: to process info_block to get requirements


            yield loader.load_item()


    @staticmethod
    def _get_release_date(release_date_str):
        """
        Получить представление даты в виде datetime по найденной на странице
        :param release_date_str: строка с датой
        :return: datetime, если возможно, иначе исходную строку
        """
        datetime_formats = ('%d %b, %Y', '%b %Y', '%B %Y', '%B, %Y', '%Y')
        for datetime_format in datetime_formats:
            try:
                return datetime.strptime(release_date_str, datetime_format)
            except ValueError:
                pass
        # TODO: добавить логгирование, чтобы все подобные случаи фиксить
        print("-------------{}------------".format(release_date_str))
        return release_date_str