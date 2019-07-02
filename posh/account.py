from bs4 import BeautifulSoup, FeatureNotFound
import requests


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

        authenticity_token = soup.find('input', attrs={'name': 'authenticity_token'}).get('value')

        r = self.session.post(
            'https://poshmark.com/login',
            params={
            'utf8': '✓',
            'authenticity_token': authenticity_token,
            'login_form[iobb]': None,
            'login_form[username_email]': self.username,
            'login_form[password]': self.password
            })

    def check_login(self):
        r = self.session.get('https://poshmark.com/feed?login=true')
        if self.username in str(r.content):
            return True
        else:
            return False
