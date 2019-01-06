# -*- coding: utf-8 -*-

"""Main module."""
from bs4 import BeautifulSoup
from collections import OrderedDict
import requests
import pytest


class Product:
    """
    An individual product on Poshmark. Can currently be built
    from either a search or (TODO instantiated with a URL directly.)
    Some attributes can only be gathered via search, while some can
    only be gathered via URL.  A product's full information can be
    gathered when the product originates from a search, but not
    when the product originates from a supplied URL.
    """

    def __init__(self, url, posted_at=None, owner=None,
                 brand=None, price=None, size=None, listing_id=None,
                 title=None, pictures=None, updated_at=None,
                 description=None, colors=None, comments=None):
        self.url = url
        self.posted_at = posted_at
        self.owner = owner
        self.brand = brand
        self.price = price
        self.size = size
        self.listing_id = listing_id
        self.title = title
        self.pictures = pictures

        # The following attributes are only available if built from URL.

        self.updated_at = updated_at
        self.description = description
        self.colors = colors
        self.comments = comments

        self._built_from = None

    def _prepare_for_db_insert(self):
        if self._built_from == 'tile':
            self.update('url')

    def _build_product_from_tile(self, tile):
        """
        Builds products from tiles, i.e. returned search results.
        """
        self._built_from = 'tile'

        self.posted_at = tile['data-created-at']
        self.owner = tile['data-creator-handle']
        self.brand = tile['data-post-brand']
        self.price = tile['data-post-price']
        self.size = tile['data-post-size']
        self.listing_id = tile['id']
        self.title = tile.find('a')['title']

    def _build_product_from_url(self, session):
        # TODO
        self._built_from = 'url'

        soup = BeautifulSoup(session.get(self.url).content, 'lxml')
        self.posted_at = 'Products built from URL don\'t have this attr.'
        self.owner = soup.find('div', class_='handle').text[1:]
        self.brand = soup.find('meta', attrs={'property': 'poshmark:brand'}
                               ).get('content')
        self.price = float(soup.find('meta',
                                     attrs={'property': 'poshmark:price'}
                                     ).get('content'))
        self.size = [i.text.strip() for i in
                     soup.find('div', class_='size-con').find_all('label')]
        self.listing_id = self.url.split('-')[-1]
        self.title = soup.find('h1', class_='title').text

    def update(self, session, built_from='tile'):
        if built_from == 'tile':
            self._build_product_from_url(self.url, session)


class ProductSearch:
    """
    May change substantially in future versions. Currently,
    handles one search and it's results.
    """

    def __init__(self):
        self.session = requests.Session()
        self.set_headers()
        self.results = []

    def _format_argument(self, argument, value, addition):
        if argument == 'subcategory':
            addition = addition.replace(' ', '_')
        elif argument == 'brand':
            addition = addition.replace(' ', '_')
        return addition

    def _build_request(self, arguments: dict):
        """
        May change substantially in future versions.
        Currently creates the string for a search given
        a dict with at least one possible_argument.
        """

        string = 'https://poshmark.com/'
        possible_arguments = OrderedDict(
            {'brand': 'brand/',
             'sex': '-',
             'category': '-',
             'subcategory': '-',
             'color': '-color-',
             'sort': '?sort_by=',
             'size': '&size%5B%5D=',
             'type': '&condition=',
             'price': '&price%5B%5D='}
        )
        for argument, value in possible_arguments.items():
            if argument == 'sort' and not arguments.get(argument):
                string += possible_arguments['sort'] + 'added_desc'
            elif arguments.get(argument):
                addition = possible_arguments[argument] + arguments[argument]
                addition = self._format_argument(argument, value, addition)
                string += addition

        return string

    def set_headers(self, headers=None):
        """
        If provided, sets headers. Otherwise,
        sets User-Agent to "Posh"
        """

        if not headers:
            headers = {'User-Agent': 'Posh'}

        self.session.headers.update(headers)

        return

    def execute_search(self, request_str, page_number=None, items=None):
        """
        Given a request_str, executes the associated search.
        Gathers results, turns their HTML into Product objects,
        then adds them to the ProductSearch object's results attr.
        """

        if page_number:
            request_str += f'&max_id={page_number}'

        r = self.session.get(request_str)

        soup = BeautifulSoup(r.content, 'lxml')
        tiles = soup.find_all('div', class_='tile')
        for tile in tiles:
            p = Product(
                url=f"https://poshmark.com{tile.find('a').get('href')}")
            p._build_product_from_tile(tile)
            self.results.append(p)

        return

    def search_multiple_pages(self, pages, arguments):
        request_str = self._build_request(arguments)
        for page in range(1, pages + 1):
            old_results_len = len(self.results)
            self.execute_search(request_str, str(page), self.results)
            new_results_len = len(self.results)
            if new_results_len == old_results_len:
                return
