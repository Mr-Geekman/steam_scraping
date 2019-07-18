# -*- coding: utf-8 -*-
import os

import yaml

# Scrapy settings for steamscraping project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'steamscraping'

SPIDER_MODULES = ['steamscraping.spiders']
NEWSPIDER_MODULE = 'steamscraping.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'steamscraping (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'steamscraping.middlewares.SteamscrapingSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'steamscraping.middlewares.SteamscrapingDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'steamscraping.pipelines.SteamscrapingPipeline': 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 4.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# ------------ My Parameters ------------ #

# For filtering snr get-parameter

DUPEFILTER_CLASS = 'steamscraping.middlewares.SteamDupeFilter'

# Crawl settings

DAYS_EARLIER = 2
REVIEWS_TO_PASS = 500

# DB settings

# TODO: to test it
APP_DIR = os.path.dirname(os.path.abspath(__file__))

class DBConfigParser:
    """
    Class for parsing database settings from config file
    """
    def __init__(self):
        db_config_filename = os.path.join(APP_DIR, 'db_config.yaml')
        if os.path.isfile(db_config_filename):
            try:
                with open(db_config_filename, 'r') as file:
                    self.data = yaml.safe_load(file)
            except Exception as e:
                raise Exception("There is some problem with "
                                "your database config file. "
                                "Run setup.py again. "
                                "Error: {}".format(e))
        else:
            raise Exception("You haven't setup this app."
                            "Please, run setup.py")

    @property
    def host(self) -> str:
        return self.data['host']

    @property
    def port(self) -> int:
        return self.data['port']

    @property
    def user(self) -> str:
        return self.data['user']

    @property
    def password(self) -> str:
        return self.data['password']
