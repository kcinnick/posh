#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `posh` package."""
import pytest

from posh.account import Account, LoginError
from posh.product_search import ProductSearch
from posh.product import Product, get_past_date

product_search = ProductSearch()


@pytest.mark.skip(reason="Not always working re: cloudflare issues.")
def test_account_login():
    test_account = Account(username='ntucker12312', password='testing_for_posh1')
    with pytest.raises(LoginError):
        test_account.check_login()
    test_account.login()
    assert test_account.check_login()


@pytest.mark.skip(reason="Not always working re: cloudflare issues.")
def test_product_like():
    #  Because Poshmark uses ReCAPTCHA, this test will fail unless the user is
    #  already logged in to the Poshmark website.
    test_account = Account(username='ntucker12312', password='testing_for_posh1')
    test_account.login()

    product = Product(url='https://poshmark.com/listing/Lularo' +
                      'e-Carly-5c2d86fcbaebf68a9b6893b0')
    product._build_product_from_url(product_search.session)

    assert product.like(test_account)
