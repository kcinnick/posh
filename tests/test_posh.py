#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `posh` package."""

import pytest

from collections import OrderedDict

from random import random

from posh.posh import ProductSearch, Product


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
        assert test_string == 'https://poshmark.com/brand/LuLaRoe-Women-Dresses-Mini-color-Black?sort_by=added_desc&size%5B%5D=M&condition=closet&price%5B%5D=26-50'


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
        assert test_string == 'https://poshmark.com/brand/LuLaRoe-Wo' + \
            'men-Dresses-Mini-color-Black?sort_by=added_desc' + \
            '&size%5B%5D=M&condition=closet&price%5B%5D=26-50'
        product_search.execute_search(test_string, page_number=1)
        assert len(product_search.results) == 15
        product_search.results = []
    product_search.execute_search(test_string, page_number=25)
    assert len(product_search.results) == 0


def test_build_product_from_url():
    product = Product(url='https://poshmark.com/listing/Lularo' +
                      'e-Carly-5c2d86fcbaebf68a9b6893b0')
    product._build_product_from_url(product_search.session)
    assert product.owner == 'cmunger81'
    assert product.brand == 'LuLaRoe'
    assert product.price == 35.0
    assert product.size == ['S']


def test_search_multiple_pages():
    product_search.search_multiple_pages(50, arguments={
        'brand': 'Vera Bradley',
        'size': 'OS',
        'sex': 'Women',
        'category': 'Bags',
        'subcategory': 'Laptop Bags',
        'color': 'Pink'
    })
    assert len(product_search.results) == 549
