#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `posh` package."""

import pytest

from collections import OrderedDict

from random import random

from posh.posh import ProductSearch


product_search = ProductSearch()


def test_build_request():
    possible_arguments = OrderedDict({
        'brand': 'LuLaRoe',
        'sex': 'Women',
        'category': 'Dresses',
        'subcategory': 'Mini',
        'color': 'Black',
        'size': 'M',
        'sort': 'added_desc',
        'type': 'closet',
        'price': '26-50'
    })

    possible_arguments = dict(sorted(possible_arguments.items(),
                                     key=lambda x: random()))

    # Make sure that arguments are ordered correctly
    # regardless of supplied order.

    for i in range(1, 5):
        possible_arguments = dict(sorted(possible_arguments.items(),
                                         key=lambda x: random()))
        test_string = product_search._build_request(possible_arguments)
        assert test_string == 'https://poshmark.com/brand/LuLaRoe-Women-D' +\
            'resses-Mini-color-Black-size-M?sort_by=add' + \
            'ed_desc&condition=closet&price%5B%5D=26-50'


def test_execute_search():
    possible_arguments = OrderedDict({
        'brand': 'LuLaRoe',
        'sex': 'Women',
        'category': 'Dresses',
        'subcategory': 'Mini',
        'color': 'Black',
        'size': 'M',
        'sort': 'added_desc',
        'type': 'closet',
        'price': '26-50'
    })

    possible_arguments = dict(sorted(possible_arguments.items(),
                                     key=lambda x: random()))
    for i in range(1, 5):
        possible_arguments = dict(sorted(possible_arguments.items(),
                                         key=lambda x: random()))
        test_string = product_search._build_request(possible_arguments)
        assert test_string == 'https://poshmark.com/brand/LuLaRoe-Women-D' +\
            'resses-Mini-color-Black-size-M?sort_by=add' + \
            'ed_desc&condition=closet&price%5B%5D=26-50'
        product_search.execute_search(test_string, page_number=2)
        assert len(product_search.results) == 48
        product_search.results = []
