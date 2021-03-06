====
posh
====


.. image:: https://img.shields.io/pypi/v/posh.svg
        :target: https://pypi.python.org/pypi/posh

.. image:: https://img.shields.io/travis/kcinnick/posh.svg
        :target: https://travis-ci.org/kcinnick/posh

.. image:: https://readthedocs.org/projects/posh/badge/?version=latest
        :target: https://posh.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




Not-yet-totally-fully-featured Poshmark bot/scraper/etc. (now available on pip!)


* Free software: MIT license
* Documentation: https://posh.readthedocs.io.


Features
----------------------

* Build products from URL 
* Build products from search results
* Build products from arbitrary string searches
* Get images, size, brand, price, and more from products.
* Search with as many (or few!) arguments as you want!
* Insert product information into any database for long-term analysis
* Easily graph historical price information for any search.

Login
----------------------
Login is tricky - it works for me about 80% of the time.  I've found a few things that help - signing in on the website and then using the script seems to work sometimes, but other times it'll just lock you out until you solve a CAPTCHA.  This could be mitigated by using a professional service like 2captcha, but I'd like to keep this project light and not rely on things like subscriptions, so I'd prefer the chance of login failing than having to pay to make sure it works 100%. 


"Why isn't X a feature"
----------------------
Because I haven't thought of it, but I'd appreciate the suggestion!


Credits
----------------------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

Development Goals
----------------------

As of now, my goal for this project is just to extend it out as much as makes sense by thinking of new ideas, methods, and functions that'd be useful or interesting.  Ideally, down the road this module could answer questions like "What was the average selling price of a new-with-tag Vera Wang dress over the last 6 months," which could inform you to buy one because it's relatively cheap or sell one because it's relatively expensive now compared to the average.  So, I don't really have definitive guidelines of where this will go.  That's the fun part!
