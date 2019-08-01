import re
from datetime import datetime

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst

from steamscraping.items import Game, str_to_date
from steamscraping.settings import DAYS_EARLIER


class GameItemLoader(ItemLoader):
    """
    Кастомный загрузчик с переопределенным output_processor по-умолчанию
    """
    default_input_processor = TakeFirst()


# TODO: see below
# 1) Доставать теги, specs
# 2) Подрубить русский язык при парсинге, если возможно
# 3) Доставать системки и ощищать их
# 4) Реализовать пайплайны для заполнения БД
# 5) Подумать над логгированием
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

    @staticmethod
    def add_cookies(request):
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
            release_date = str_to_date(release_date_str)

            if (isinstance(release_date, datetime) and
                    (datetime.now() - release_date).days <= DAYS_EARLIER):
                return self.parse(response)

        pass

    @staticmethod
    def parse_game(response):
        """
        Метод для парсинга самой игры
        """
        # если появляется форма выбора возраста, значит сломались куки
        if '/agecheck/app' in response.url:
            # TODO: добавить логгирование
            print("--------COOKIES BROKEN--------")

        # если формы ввода возраста нет, то все делаем,как обычно
        else:
            loader = GameItemLoader(item=Game(), response=response)

            loader.add_css('div.date ::text')

            game_id = int(re.match(r'.+/(\d+)/.+', response.url).groups()[0])
            loader.add_value('game_id', game_id)

            loader.add_css('title', '.apphub_AppName ::text')

            loader.add_css('description', '#game_area_description')

            loader.add_css('num_reviews',
                           '.user_reviews .responsive_hidden ::text')

            loader.add_css('specs', '.game_area_details_specs a ::text')

            loader.add_css('tags', 'a.app_tag ::text')

            loader.add_css('price', 'div.price::attr(data-price-final)')

            yield loader.load_item()
