#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `posh` package."""
import pytest

from bs4 import BeautifulSoup, FeatureNotFound

from collections import OrderedDict
import datetime
from dateutil.relativedelta import relativedelta

from random import random
from requests import get

from posh.posh import ProductSearch, Product, get_past_date

#from sqlalchemy import create_engine
#from sqlalchemy.orm import scoped_session, sessionmaker

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
        assert len(product_search.results) > 10
        product_search.results = []
    product_search.execute_search(possible_arguments, page_number=25)
    assert len(product_search.results) == 0


def test_build_product_from_url():
    product = Product(url='https://poshmark.com/listing/Lularo' +
                      'e-Carly-5c2d86fcbaebf68a9b6893b0')
    product._build_product_from_url(product_search.session)
    assert product.owner == 'cmunger81'
    assert product.brand == 'LuLaRoe'
    assert product.price == 32.0
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
                    'Updated an hour ago', 'Updated 3 days ago',
                    'Updated Yesterday']

    for string in test_strings:
        assert type(get_past_date(string)) == datetime.datetime

    with pytest.raises(ValueError):
        string = "Updated 90 eons ago."
        get_past_date(string)

    assert get_past_date('Updated 3 hours ago').hour == \
        (datetime.datetime.today() - relativedelta(hours=3)).hour

    assert type(get_past_date('Updated 9/27/2018')) == datetime.datetime


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

    first_result.update(product_search.session)

    assert isinstance(first_result.description, str)


@pytest.mark.skip(reason="Needs to be customized to each user's DB instance.")
def test_insert_into_db():
    engine = create_engine(
        "postgres:///nick:nickspassword@localhost/test:5432")

    connection = engine.connect()

    db_session = scoped_session(sessionmaker(
        autocommit=True, autoflush=True, bind=engine))

    product = Product(url='https://poshmark.com/listi' +
                      'ng/Lularoe-Carly-5c2d86fcbaebf68a9b6893b0')
    product._build_product_from_url(product_search.session)

    product.insert_into_db(db_session)


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
        soup = BeautifulSoup(r.content)

    assert soup.find_all(
        'span', attrs={'itemprop': 'name'})[1].text == 'Makeup'

    # The second span with name itemprop is the currently selected category.


def test_get_pictures():
    product = Product(url='https://poshmark.com/listing/Lularo' +
                      'e-Carly-5c2d86fcbaebf68a9b6893b0')
    product._build_product_from_url(product_search.session)
    assert len(product.pictures) == 1


def test_get_images():
    product = Product(url='https://poshmark.com/listing/Lularo' +
                      'e-Carly-5c2d86fcbaebf68a9b6893b0')
    product._build_product_from_url(product_search.session)
    product.get_images()

    assert product.images[0] == 'Lularoe Carly-5c2d86fcbaebf68a9b6893b0-cmunger81_0.jpg'