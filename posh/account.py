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
        try:
            if self.check_login():
                print('You\'re already logged in!\n')
                return
        except LoginError:
            pass
        r = self.session.get('https://poshmark.com/login')
        try:
            soup = BeautifulSoup(r.content, 'lxml')
        except FeatureNotFound:
            soup = BeautifulSoup(r.content)

        try:
            authenticity_token = soup.find('meta', attrs={'id': 'csrftoken'}).get('content')
        except AttributeError:
            if '"userInfo":{"dh":"%s"' % self.username in str(soup):
                print('Logged in..\n')
                return

        r = self.session.post(
            'https://poshmark.com/login',
            params={
                'utf8': '✓',
                'authenticity_token': authenticity_token,
                'login_form[iobb]': None,
                'login_form[username_email]': self.username,
                'login_form[password]': self.password
            })

        print(r.content)
        assert self.check_login()

        return

    def check_login(self):
        # TODO: This is repeated code (lines 28-53 - clean that up.)
        r = self.session.get('https://poshmark.com/login')
        try:
            soup = BeautifulSoup(r.content, 'lxml')
        except FeatureNotFound:
            soup = BeautifulSoup(r.content)

        if '"userInfo":{"dh":"%s"' % self.username in str(soup):
            print('Logged in..\n')
            return True
