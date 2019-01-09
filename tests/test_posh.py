#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `posh` package."""

import pytest

from collections import OrderedDict
import datetime

from random import random

from posh.posh import ProductSearch, Product, get_past_date


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
        assert test_string == 'https://poshmark.com/brand/LuLaRoe-Wom' + \
            'en-Dresses-Mini-color-Black?sort_by=added_des' + \
            'c&size%5B%5D=M&condition=closet&price%5B%5D=26-50'


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

    for i in range(1, 5):
        possible_arguments = dict(sorted(possible_arguments.items(),
                                         key=lambda x: random()))
        product_search.execute_search(possible_arguments, page_number=1)
        assert len(product_search.results) == 15
        product_search.results = []
    product_search.execute_search(possible_arguments, page_number=25)
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
    assert len(product_search.results) >= 545
    # More products are added all the time so it'd be tricky to pin
    # down an exact number that wouldn't require changing all the time.
    # However, the search should always return >545 unique items.
    # May need to be changed in the future if Vera Bradley goes out
    # of style. (possibly occurred already?)


def test_product_update():
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
    product_search.execute_search(possible_arguments)

    first_result = product_search.results[0]
    assert first_result.updated_at is None
    first_result.update(product_search.session, built_from='tile')
    assert isinstance(first_result.updated_at, datetime.datetime)


def test_get_past_date():
    test_strings = ['Updated 3 minutes ago', 'Updated 3 hours ago',
                    'Updated 3 days ago']
    for string in test_strings:
        assert type(get_past_date(string)) == datetime.datetime

    with pytest.raises(ValueError):
        string = "Updated 90 eons ago."
        get_past_date(string)


def test_prepare_for_db_insert():
    arguments = OrderedDict({
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

    product_search.execute_search(arguments)

    first_result = product_search.results[1]

    assert first_result.description is None

    first_result._prepare_for_db_insert()
    assert isinstance(first_result.description, str)
