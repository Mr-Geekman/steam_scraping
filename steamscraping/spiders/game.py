import re
from datetime import datetime

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst

from steamscraping.items import Game, StrToDate
import steamscraping.settings as settings


class GameItemLoader(ItemLoader):
    """Custom item loader with overrided default output_processor."""
    default_output_processor = TakeFirst()


# TODO: see below
# 1) make pipelines
# 2) write tests
# 3) think carefully about switching language
# 4) think about logging
# 5) add sections to config files
class GameParser(CrawlSpider):
    """Spider class for parsing new games."""
    name = 'games'
    start_urls = ["https://store.steampowered.com/search/"
                  "?sort_by=Released_DESC&category1=998"]
    allowed_domains = ['steampowered.com']
    selectors = {'release_date': 'div.date ::text',
                 'title': '.apphub_AppName ::text',
                 'description': '#game_area_description',
                 'num_reviews': '.user_reviews .responsive_hidden ::text',
                 'specs': '.game_area_details_specs a ::text',
                 'tags': 'a.app_tag ::text',
                 'price': 'div.price::attr(data-price-final)',
                 'system_requirements':
                     '.game_area_sys_req[data-os="win"] ::text'
                 }

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
        """Add cookies.

         We can do it to set correct language, avoiding age checking,
         mature content checking
         """
        request.cookies.update({'Steam_language': settings.LANGUAGE,
                                'mature_content': '1',
                                'lastagecheckage': '1-0-2000',
                                'birthtime': 943999201})

        return request

    def parse_page(self, response):
        """Method for parsing page with games.

        We should stop parsing if we face too old game (depends on settings)
        """
        # look at games release dates on the page
        # if there is at least one game, that released in relevant time
        # process the page
        release_dates_str = response.css('div.search_released::text').extract()
        for release_date_str in release_dates_str:
            release_date = StrToDate()(release_date_str)
            if isinstance(release_date, datetime):
                days_difference = (datetime.now() - release_date).days
                if days_difference <= settings.DAYS_EARLIER:
                    return self.parse(response)
        pass

    def parse_game(self, response):
        """Method for parsing game."""
        # if there is age checking form, than our cookies broke
        if '/agecheck/app' in response.url:
            # TODO: add logging
            print("--------COOKIES BROKEN--------")

        # if other case, process the page
        else:
            loader = GameItemLoader(item=Game(), response=response)

            game_id = self._find_id_by_url(response.url)
            loader.add_value('game_id', game_id)

            for field, selector in self.selectors:
                loader.add_css(field, selector)

            yield loader.load_item()

    @staticmethod
    def _find_id_by_url(response):
        """Finding id of game in game url."""
        return int(re.search(r'.+/(\d+)/.+', response.url).group(0))
