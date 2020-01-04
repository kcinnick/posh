#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `posh` package."""

from collections import OrderedDict
from random import random

from bs4 import BeautifulSoup, FeatureNotFound
from requests import get
#from sqlalchemy import create_engine
#from sqlalchemy.orm import scoped_session, sessionmaker

from posh.product_search import ProductSearch

product_search = ProductSearch()  # TODO: make this a fixture


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
        assert len(product_search.results) > 10
        product_search.results = []
    product_search.execute_search(possible_arguments, page_number=47)
    assert len(product_search.results) == 0


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


def test_brand_search():
    product_search.results = []
    product_search.search_multiple_pages(1, arguments={
        'brand': 'rag & bone'
        })
    for result in product_search.results:
        assert result.brand.lower() == 'rag & bone'


def test_search_by_query():
    product_search.results = []

    arguments = OrderedDict({
        'query': 'signed jersey'
    })

    product_search.execute_search(arguments)
    #  It should be made clear somewhere that this method searches
    #  for items exactly the same as if the search occurred on Poshmark.com
    #  - which means that all sorts of non-jersey products get included
    #  in this search.  Consider adding a filter arg to include
    #  only items with query in title, etc. instead of trusting
    #  Poshmark's search.

    result = any([i.title.lower() for i in product_search.results
                  if 'jersey' in i.title.lower()])
    assert result


def test_category_search():
    product_search.results = []

    arguments = {'category': 'Makeup',
                 'sex': 'Women'}

    request_str = product_search._build_request(arguments)

    r = get(request_str, headers={'User-Agent': 'Posh'})

    try:
        soup = BeautifulSoup(r.content, 'lxml')
    except FeatureNotFound:
        soup = BeautifulSoup(r.content, 'html.parser')

    assert soup.find_all(
        'span', attrs={'itemprop': 'name'})[1].text == 'Makeup'


def test_strict_search():
    product_search.results = []
    product_search.search_multiple_pages(pages=2, arguments={
        'query': 'signed jersey'
    }, strict=True)

    assert all(['signed jersey' in i.title.lower()
                for i in product_search.results])


def test_search_over_time():
    product_search.results = []
    product_search.search_product_price_over_time(arguments=OrderedDict({
        'query': 'NWT vera wang'}
    ), strict=False)
    assert len(product_search.results) >= 500
