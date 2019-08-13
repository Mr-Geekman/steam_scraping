import datetime
from unittest.mock import patch

import pytest
import freezegun

from steamscraping.spiders.game import GameParser
from tests.conftest import fake_response_from_file
from steamscraping import settings


class TestParsePage:
    """
    Test class for testing parsing page.
    """
    spider = GameParser()

    @staticmethod
    def setup_class():
        """Set up class before using it."""
        settings.DAYS_EARLIER = 1

    @freezegun.freeze_time('2019-08-14')
    @pytest.mark.parametrize('test_input', 'expected', [()])
    @patch('steamscraping.spiders.game.GameParser.parser', return_value=True)
    def test_page(self, test_input, expected):
        returned = self.spider.parse(fake_response_from_file(test_input))

        assert returned == expected


class TestParseGame:
    """
    Test class for testing parsing game.
    """
    pass
