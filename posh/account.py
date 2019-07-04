from bs4 import BeautifulSoup, FeatureNotFound
import requests


class LoginError(AssertionError):
    def __init__(self, message, errors):

        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        # Now for your custom code...
        self.errors = errors


class Account:
    def __init__(self, username, password, session=requests.Session()):
        self.username = username
        self.password = password
        self.session = session

    def login(self):
        r = self.session.get('https://poshmark.com/login')
        try:
            soup = BeautifulSoup(r.content, 'lxml')
        except FeatureNotFound:
            soup = BeautifulSoup(r.content)

        try:
            authenticity_token = soup.find('input', attrs={'name': 'authenticity_token'}).get('value')
        except AttributeError:
            if '"userInfo":{"dh":"%s"' % self.username in str(soup):
                print('Logged in..\n')
                return
            else:
                raise LoginError

        r = self.session.post(
            'https://poshmark.com/login',
            params={
            'utf8': '✓',
            'authenticity_token': authenticity_token,
            'login_form[iobb]': None,
            'login_form[username_email]': self.username,
            'login_form[password]': self.password
            })

        try:
            assert self.check_login()
        except LoginError:
            print('Login failed: {}'.format(r.content))

    def check_login(self):
        # Find a cleaner way to map these if/elif blocks throughout code
        r = self.session.get('https://poshmark.com/feed?login=true')
        if self.username in str(r.content):
            return True
        else:
            raise LoginError(message='You aren\'t logged in.', errors='You aren\'t logged in.')
