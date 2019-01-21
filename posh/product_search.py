from bs4 import BeautifulSoup, FeatureNotFound
from collections import OrderedDict
import datetime
from dateutil.relativedelta import relativedelta
from posh.product import Product
import operator
import requests
import time


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def datestring_to_timestamp(str):
    return time.mktime(time.strptime(str, "%Y-%m-%d %H:%M:%S %z"))


def timestamp_to_datestring(timestamp):
    return time.strftime('%Y-%m-%d %H:%M:%S %z', time.localtime(timestamp))


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

        if 'max_id' in arguments.keys():
            string = string.replace(
                'search?query', f'search?max_id={arguments["max_id"]}&query')

        #  Too many statements to accomplish proper string mashing.
        #  Find a way to tighten the above.

        return string

    def _check_strictness(self, tile, arguments):
        title = tile.find('h4').text.lower()
        for key, value in arguments.items():
            if str(value).lower() not in title:
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
        if page_number:
            if page_number == 1:
                pass
            else:
                arguments.update({'max_id': int(page_number)})

        request_str = self._build_request(arguments)

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
        for page in range(1, pages + 1):
            old_results_len = len(self.results)
            self.execute_search(arguments=arguments, page_number=page,
                                items=self.results, strict=strict)
            new_results_len = len(self.results)
            if not strict:
                if new_results_len == old_results_len:
                    return

    def search_product_price_over_time(self, arguments, strict=False):
        self.search_multiple_pages(
            arguments=arguments, pages=48, strict=strict)
        time_sorted_products = sorted(
            self.results, key=operator.attrgetter('posted_at'))

        for product_chunk in chunks(time_sorted_products, 25):
            avg_time = float(sum([
                datestring_to_timestamp(i.posted_at)
                for i in product_chunk])) / max(len(product_chunk), 1)
            avg_price = sum(
                [float(i.price.replace('$', '').replace(',', ''))
                 for i in product_chunk])
            print(timestamp_to_datestring(avg_time), avg_price)
