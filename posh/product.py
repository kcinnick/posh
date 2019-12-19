from bs4 import BeautifulSoup, FeatureNotFound
import datetime
from dateutil.parser import parse as date_parser
from dateutil.relativedelta import relativedelta
import os


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
        if 'a minute' in split_str[2]:
            return datetime.datetime.now() - \
                   datetime.timedelta(minutes=1)
        elif 'seconds ago' in split_str[2]:
            return datetime.datetime.now() - \
                   datetime.timedelta(minutes=1)
        elif 'minute' in split_str[2]:
            if split_str[1] == 'a':
                split_str[1] = 1
            return datetime.datetime.now() - \
                datetime.timedelta(minutes=int(split_str[1]))

        elif 'hour' in split_str[2]:
            date = datetime.datetime.now() - \
                relativedelta(hours=int(split_str[1]))
            return date

        elif 'day' in split_str[2]:
            date = today - relativedelta(days=int(split_str[1]))
            return date

        if 'seconds' in str_days_ago:
            return datetime.datetime.now() - \
                   datetime.timedelta(minutes=1)
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
        self.price = float(tile['data-post-price'].replace('$', '').replace(',', ''))
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
            soup = BeautifulSoup(session.get(self.url).content, 'html.parser')

        self.__soup = soup
        self._get_pictures()

        self.owner = soup.find('div', class_='handle').text[1:]
        self.brand = soup.find('meta', attrs={'property': 'product:brand'}
                           ).get('content')
        self.price = float(soup.find('meta',
                                     attrs={'property': 'product:price:amount'}
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
                    self.session.get(self.url).content, 'html.parser')

        pictures = self.__soup.find_all('img', attrs={'itemprop': 'image'})
        picture_urls = [i.get('data-img-src') for i in pictures if i.get(
            'data-img-src')]
        self.pictures = picture_urls
        return

    def get_images(self, folder_path=None):
        self.images = []
        if len(self.pictures) == 0:
            self._get_pictures()

        for index, link in enumerate(self.pictures):
            r = self.session.get(link)
            file_name = \
                f'{self.title}-{self.listing_id}-{self.owner}_{index}.jpg'
            if folder_path:
                if not os.path.isdir(folder_path):
                    os.mkdir(folder_path)
                file_name = f'{folder_path}/{file_name}'
            with open(file_name, 'wb') as f:
                f.write(r.content)
                self.images.append(file_name)

    def like(self, account):
        # Like URL is internally referred to as listing_id
        listing_id = self.url.split('-')[-1]
        product_like_url = f"https://poshmark.com/listing/{listing_id}/like"
        account.login()
        # Should we leave logging in up to the user's judgment? Or force a login?
        # Current approach is to force it.
        r = account.session.get(product_like_url)
        if 'success' in str(r.content):
            return True
        else:
            return False

