# -*- coding: utf-8 -*-

"""Main module."""
from bs4 import BeautifulSoup
from collections import OrderedDict
import requests


class Product:
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
        self.posted_at = tile['data-created-at']
        self.owner = tile['data-creator-handle']
        self.brand = tile['data-post-brand']
        self.price = tile['data-post-price']
        self.size = tile['data-post-size']
        self.listing_id = tile['id']
        self.title = tile.find('a')['title']


class ProductSearch:
    def __init__(self, sex=None, category=None, sizes=None, colors=None,
                 prices=None, subcategory=None, condition=None,
                 availability=None):
        self.session = requests.Session()
        self.set_headers()
        self.category = category
        self.sizes = sizes
        self.colors = colors
        self.prices = prices
        self.subcategory = subcategory
        self.condition = condition
        self.availability = availability
        self.results = []

    def set_headers(self, headers=None):
        if not headers:
            headers = {'User-Agent': 'Posh'}

        self.session.headers.update(headers)

        return

    def _build_request(self, arguments: dict):
        string = 'https://poshmark.com/'
        possible_arguments = OrderedDict(
            {'brand': 'brand/',
             'sex': '-',
             'category': '-',
             'subcategory': '-',
             'color': 'color-',
             'size': 'size-',
             'sort': '?sort_by=',
             'type': '-'}
        )
        for argument, value in possible_arguments.items():
            if arguments.get(argument):
                addition = possible_arguments[argument] + arguments[argument]
                string += addition

        return string

    def execute_search(self, request_str, page_number=None, items=None):
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
