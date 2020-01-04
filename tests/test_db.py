from collections import OrderedDict
import datetime
import pytest

from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from posh.product_search import ProductSearch
from posh.product import Product, get_past_date

product_search = ProductSearch()


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

