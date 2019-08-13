import os

from scrapy.http import Response, Request

from steamscraping.settings import APP_DIR


def fake_response_from_file(file_name, url=None):
    """
    Create a Scrapy fake HTTP response from a HTML file.

    :param file_name: The relative filename from the responses directory,
                      but absolute paths are also accepted.
    :param url: The URL of the response.
    :returns: A scrapy HTTP response which can be used for unittesting.
    """
    if not url:
        url = 'https://store.steampowered.com'

    request = Request(url=url)
    file_path = os.path.join(APP_DIR, 'tests', 'responses', file_name)
    file_content = open(file_path, 'r').read()

    response = Response(url=url, request=request, body=file_content)
    response.encoding = 'utf-8'
    return response


