from collections import OrderedDict
import datetime
import pytest
import os

from dateutil.relativedelta import relativedelta

from posh.product_search import ProductSearch
from posh.product import Product, get_past_date

product_search = ProductSearch()


def test_get_pictures():
    product = Product(url='https://poshmark.com/listing/Lularo' +
                      'e-Carly-5c2d86fcbaebf68a9b6893b0')
    product._build_product_from_url(product_search.session)
    assert len(product.pictures) == 1


def test_get_images():
    product = Product(url='https://poshmark.com/listing/Lularo' +
                      'e-Carly-5c2d86fcbaebf68a9b6893b0')
    product._build_product_from_url(product_search.session)
    product.get_images(folder_path=os.curdir)

    assert 'Lularoe Carly-5c2d86fcbaebf68a9b6893' + \
        'b0-cmunger81_0.jpg' in product.images[0]


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


def test_build_product_from_url():
    product = Product(url='https://poshmark.com/listing/Lularo' +
                      'e-Carly-5c2d86fcbaebf68a9b6893b0')
    product._build_product_from_url(product_search.session)
    assert product.owner == 'cmunger81'
    assert product.brand == 'LuLaRoe'
    assert product.price == 25.0
    assert product.size == ['S']


@pytest.mark.skip(reason="Need to find a way to actually test this.")
def test_plot_time_price_tuples():
    product_search.results = []
    product_search.search_product_price_over_time(arguments=OrderedDict({
        'query': 'NWT vera wang'}
    ), strict=False)
    product_search.plot_time_price_tuples()
