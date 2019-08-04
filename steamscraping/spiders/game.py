import re
from datetime import datetime

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst

from steamscraping.items import Game, StrToDate
from steamscraping.settings import DAYS_EARLIER, LANGUAGE


class GameItemLoader(ItemLoader):
    """
    Custom item loader with overrided default output_processor
    """
    default_input_processor = TakeFirst()


# TODO: see below
# 1) make pipelines
# 2) write tests
# 3) think carefully about switching language
# 4) think about logging
# 5) add sections to config files
class GameParser(CrawlSpider):
    """
    Spider class for parsing new games
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
        Add cookie for correct language, avoiding age checking,
            mature content checking
        """
        request.cookies.update({'Steam_language': LANGUAGE,
                                'mature_content': '1',
                                'lastagecheckage': '1-0-2000',
                                'birthtime': 943999201})

        return request

    def parse_page(self, response):
        """
        Method for parsing page with games
        We should stop parsing if we face too old game (depends on settings)
        """
        # look at games release dates on the page
        # if there is at least one game, that released in relevant time
        # process the page
        release_dates_str = response.css('div.search_released::text').extract()
        for release_date_str in release_dates_str:
            release_date = StrToDate()(release_date_str)

            if (isinstance(release_date, datetime) and
                    (datetime.now() - release_date).days <= DAYS_EARLIER):
                return self.parse(response)

        pass

    @staticmethod
    def parse_game(response):
        """
        Method for parsing game
        """
        # if there is age checking form, than our cookies broke
        if '/agecheck/app' in response.url:
            # TODO: add logging
            print("--------COOKIES BROKEN--------")

        # if other case, process the page
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

            loader.add_css('system_requirements',
                           '.game_area_sys_req[data-os="win"] ::text')

            yield loader.load_item()
