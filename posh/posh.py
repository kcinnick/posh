# -*- coding: utf-8 -*-

"""Main module."""
from collections import OrderedDict
import requests


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


