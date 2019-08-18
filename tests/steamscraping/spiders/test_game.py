from unittest.mock import patch, MagicMock

import pytest
import freezegun

from steamscraping.spiders.game import GameParser, GameItemLoader
from steamscraping.items import Game
from tests.conftest import fake_response_from_file
from steamscraping import settings


class TestParsePage:
    """Test class for testing parsing page."""
    spider = GameParser()

    @staticmethod
    def setup_class():
        """Set up class before using it."""
        settings.DAYS_EARLIER = 1

    @freezegun.freeze_time('2019-08-18')
    @pytest.mark.parametrize('test_input, expected',
                             [('page_1.html', True),
                              ('page_2.html', True),
                              ('page_3.html', None)])
    @patch('steamscraping.spiders.game.GameParser.parse',
           MagicMock(return_value=True))
    def test_page(self, test_input, expected):
        """Test, passing or not passing page."""
        returned = self.spider.parse_page(fake_response_from_file(test_input))
        assert returned == expected


class TestParseGame:
    """Test class for testing parsing game."""
    spider = GameParser()

    @staticmethod
    def setup_class():
        """Set up class before using it."""
        settings.DAYS_EARLIER = 1

    @pytest.mark.parametrize('test_input, expected',
                             [('title_1.html', 'Portal 2'),
                              ('title_2.html', 'STEINS;GATE')])
    @patch('steamscraping.spiders.game.GameParser._find_id_by_url',
           MagicMock(return_value=42))
    def test_title(self, test_input, expected):
        """Test finding game title."""
        response = fake_response_from_file(test_input)
        loader = GameItemLoader(item=Game(), response=response)
        loader.add_css('title', GameParser.selectors['title'])
        result = loader.load_item()
        assert result['title'] == expected
