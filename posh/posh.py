# -*- coding: utf-8 -*-

"""Main module."""
from bs4 import BeautifulSoup, FeatureNotFound
from collections import OrderedDict
import datetime
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse as date_parser
import requests


def get_past_date(str_days_ago):
    """
    Converts arbitrary "updated at" strings to proper datetimes.
    """

    str_days_ago = str_days_ago.replace(' an ', ' 1 ')

    #  When it's been <2 hours, Poshmark returns "an hour ago"
    #  instead of "1 hour ago" - which, without this replacement,
    #  screws up the later date parsing.

    today = datetime.datetime.today()
    split_str = str_days_ago.split()

    if 'Yesterday' in split_str:
        return datetime.datetime.now() - relativedelta(days=1)

    elif len(split_str) < 2:   # Could all of this be replaced by date_parser?
        date = date_parser(str_days_ago[8:])
        return date

    elif len(split_str) == 2:
        date = date_parser(str_days_ago[8:])
        return date

    elif len(split_str) > 2:
        if 'minute' in split_str[2]:
            return datetime.datetime.now() - \
                datetime.timedelta(minutes=int(split_str[1]))

        elif 'hour' in split_str[2]:
            date = datetime.datetime.now() - \
                relativedelta(hours=int(split_str[1]))
            return date

        elif 'day' in split_str[2]:
            date = today - relativedelta(days=int(split_str[1]))
            return date

        else:
            return date_parser(str_days_ago[8:])

    else:
        raise ValueError(
            f'Supplied date str is {split_str}, ' +
            'which doesn\'t match any supported formats.')


class Product:
    """
    An individual product on Poshmark. Can currently be built
    from either a search or built with a URL directly.
    Some attributes can only be gathered via search, while some can
    only be gathered via URL.  A product's full information can be
    gathered when the product originates from a search, but not
    when the product originates from a supplied URL.
    """

    def __init__(self, url, posted_at=None, owner=None,
                 brand=None, price=None, size=None, listing_id=None,
                 title=None, pictures=None, updated_at=None,
                 description=None, colors=None, comments=None):
        self.__soup = None

        self._built_from = None

        self.images = None

        self.url = url
        self.posted_at = posted_at
        self.owner = owner
        self.brand = brand
        self.price = price
        self.size = size
        self.listing_id = listing_id
        self.title = title
        self.pictures = pictures
        self.updated_at = updated_at

        # The following attributes are only available if built from URL.

        self.description = description
        self.colors = colors
        self.comments = comments

    def insert_into_db(self, db_session, table_name='product'):
        self.update(self.session)
        query = f""" \
                INSERT INTO {table_name} (url, owner, brand, price,\
                size, listing_id, title, pictures, description,\
                colors, comments, built_from)
                VALUES
                (\
                '{self.url}', '{self.owner}','{self.brand}',
                 {self.price}, '{', '.join([i for i in self.size])}',
                 '{self.listing_id}',
                 '{self.title}', '{self.pictures}',
                 '{self.description}', '{self.colors}', '{self.comments}',
                 '{self._built_from}')
                """
        db_session.execute(query)
        return

    def _build_product_from_tile(self, tile, session):
        """
        Builds products from tiles, i.e. returned search results.
        """

        self.session = session  # This is lazy
        self._built_from = 'tile'

        self.posted_at = tile['data-created-at']
        self.owner = tile['data-creator-handle']
        self.brand = tile.get('data-post-brand')  # Not always there.
        self.price = tile['data-post-price']
        self.size = tile['data-post-size']
        self.listing_id = tile['id']
        self.title = tile.find('a')['title']

    def _build_product_from_url(self, session):
        self.session = session  # This is lazy

        if not self._built_from:
            self._built_from = 'url'

        try:
            soup = BeautifulSoup(session.get(self.url).content, 'lxml')
        except FeatureNotFound:
            soup = BeautifulSoup(session.get(self.url).content)
        self.__soup = soup
        self._get_pictures()

        self.owner = soup.find('div', class_='handle').text[1:]
        self.brand = soup.find('meta', attrs={'property': 'poshmark:brand'}
                               ).get('content')
        self.price = float(soup.find('meta',
                                     attrs={'property': 'poshmark:price'}
                                     ).get('content'))
        self.size = [i.text.strip() for i in
                     soup.find('div', class_='size-con').find_all('label')]
        self.listing_id = self.url.split('-')[-1]
        self.title = soup.find('h1', class_='title').text
        updated_at = soup.find('span', class_='time').text
        self.updated_at = get_past_date(updated_at)
        self.description = soup.find('div', class_='description').text
        self.colors = None  # Not yet implemented.
        self.comments = soup.find(
            'div', class_='comments')  # Not yet fully implemented.

    def update(self, session, built_from='tile'):
        if built_from == 'tile':
            self._build_product_from_url(session)

    def _get_pictures(self):
        if not self.__soup:
            try:
                self.__soup = BeautifulSoup(
                    self.session.get(self.url).content, 'lxml')
            except FeatureNotFound:
                self.__soup = BeautifulSoup(
                    self.session.get(self.url).content)

        pictures = self.__soup.find_all('img', attrs={'itemprop': 'image'})
        picture_urls = [i.get('data-img-src') for i in pictures if i.get(
            'data-img-src')]
        self.pictures = picture_urls
        return

    def get_images(self):
        self.images = []
        if len(self.pictures) == 0:
            self._get_pictures()

        for index, link in enumerate(self.pictures):
            r = self.session.get(link)
            file_name = \
                f'{self.title}-{self.listing_id}-{self.owner}_{index}.jpg'
            with open(file_name, 'wb') as f:
                f.write(r.content)
                self.images.append(file_name)


class ProductSearch:
    """
    May change substantially in future versions. Currently,
    handles one search and it's results.
    """

    def __init__(self):
        self.session = requests.Session()
        self.set_headers()
        self.results = []

    def _format_argument(self, argument, value, addition):
        if argument == 'subcategory':
            addition = addition.replace(' ', '_')
        elif argument == 'brand':
            addition = addition.replace(' ', '_')
        elif argument == 'query':
            addition = addition.replace(' ', '+')
        return addition

    def _build_request(self, arguments: dict):
        """
        May change substantially in future versions.
        Currently creates the string for a search given
        a dict with at least one possible_argument.
        """

        string = 'https://poshmark.com/'
        possible_arguments = OrderedDict(
            {'query': 'search?query=',
             'brand': 'brand/',
             'sex': '-',
             'category': '-',
             'subcategory': '-',
             'color': '-color-',
             'sort': '?sort_by=',
             'size': '&size%5B%5D=',
             'type': '&condition=',
             'price': '&price%5B%5D='
             }
        )
        for argument, value in possible_arguments.items():
            if argument == 'sort' and not arguments.get(argument):
                string += possible_arguments['sort'] + 'added_desc'
            elif arguments.get(argument) and argument == 'query':
                addition = possible_arguments[argument] + arguments[argument]
                addition = self._format_argument(argument, value, addition)
                string += addition
            elif arguments.get(argument):
                addition = possible_arguments[argument] + arguments[argument]
                addition = self._format_argument(argument, value, addition)
                string += addition

        if string[21] == '-':
            if 'category' in arguments.keys():
                string = string[:21] + 'category/' + string[22:]

        if 'query' in string:
            string = string.replace('?sort_by', '&sort_by')

        return string

    def set_headers(self, headers=None):
        """
        If provided, sets headers. Otherwise,
        sets User-Agent to "Posh"
        """

        if not headers:
            headers = {'User-Agent': 'Posh'}

        self.session.headers.update(headers)

        return

    def execute_search(self, arguments, page_number=None, items=None):
        """
        Given a request_str, executes the associated search.
        Gathers results, turns their HTML into Product objects,
        then adds them to the ProductSearch object's results attr.
        """

        request_str = self._build_request(arguments)

        if page_number:
            request_str += f'&max_id={page_number}'

        r = self.session.get(request_str)

        try:
            soup = BeautifulSoup(r.content, 'lxml')
        except FeatureNotFound:
            soup = BeautifulSoup(r.content)

        tiles = soup.find_all('div', class_='tile')
        for tile in tiles:
            p = Product(
                url=f"https://poshmark.com{tile.find('a').get('href')}")
            p._build_product_from_tile(tile, self.session)
            self.results.append(p)

        return

    def search_multiple_pages(self, pages, arguments):
        request_str = self._build_request(arguments)
        for page in range(1, pages + 1):
            old_results_len = len(self.results)
            self.execute_search(arguments, str(page), self.results)
            new_results_len = len(self.results)
            if new_results_len == old_results_len:
                return
