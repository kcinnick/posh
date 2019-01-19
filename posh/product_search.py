from bs4 import BeautifulSoup, FeatureNotFound
from collections import OrderedDict
import datetime
from dateutil.relativedelta import relativedelta
from posh.product import Product
import requests


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

    def _check_strictness(self, tile, arguments):
        title = tile.find('h4').text.lower()
        for key, value in arguments.items():
            if value not in title:
                return False
            else:
                continue
        return True

    def set_headers(self, headers=None):
        """
        If provided, sets headers. Otherwise,
        sets User-Agent to "Posh"
        """

        if not headers:
            headers = {'User-Agent': 'Posh'}

        self.session.headers.update(headers)

        return

    def execute_search(self, arguments, page_number=None,
                       items=None, strict=False):
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
            strictness_pass = self._check_strictness(tile, arguments)
            if strict and strictness_pass:
                #  There needs to be a better way to do this.
                p = Product(
                    url=f"https://poshmark.com{tile.find('a').get('href')}")
                p._build_product_from_tile(tile, self.session)
                self.results.append(p)
                continue
            elif strict and not strictness_pass:
                continue
            elif not strict:
                p = Product(
                    url=f"https://poshmark.com{tile.find('a').get('href')}")
                p._build_product_from_tile(tile, self.session)
                self.results.append(p)
                continue
        return

    def search_multiple_pages(self, pages, arguments, strict=False):
        request_str = self._build_request(arguments)
        for page in range(1, pages + 1):
            old_results_len = len(self.results)
            self.execute_search(arguments=arguments, page_number=str(page),
                                items=self.results, strict=strict)
            new_results_len = len(self.results)
            if new_results_len == old_results_len:
                return
