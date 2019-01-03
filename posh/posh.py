# -*- coding: utf-8 -*-

"""Main module."""
from bs4 import BeautifulSoup
from collections import OrderedDict
import requests


class Product:
    """
    An individual product on Poshmark. Can currently be built
    from either a search or (TODO instantiated with a URL directly.)
    """

    def __init__(self, url, posted_at=None, owner=None, brand=None,
                 price=None, size=None, listing_id=None, title=None):
        self.url = url
        self.posted_at = posted_at
        self.owner = owner
        self.brand = brand
        self.price = price
        self.size = size
        self.listing_id = listing_id
        self.title = title

    def _build_product_from_tile(self, tile):
        """
        Builds products from tiles, i.e. returned search results.
        """

        self.posted_at = tile['data-created-at']
        self.owner = tile['data-creator-handle']
        self.brand = tile['data-post-brand']
        self.price = tile['data-post-price']
        self.size = tile['data-post-size']
        self.listing_id = tile['id']
        self.title = tile.find('a')['title']


class ProductSearch:
    """
    May change substantially in future versions. Currently,
    handles one search and it's results.
    """

    def __init__(self):
        self.session = requests.Session()
        self.set_headers()
        self.results = []

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
             'size': '-size-',
             'sort': '?sort_by=',
             'type': '&condition=',
             'price': '&price%5B%5D='}
        )
        for argument, value in possible_arguments.items():
            if arguments.get(argument):
                addition = possible_arguments[argument] + arguments[argument]
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
