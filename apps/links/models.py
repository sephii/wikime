import requests
from bs4 import BeautifulSoup
from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=100)


class Link(models.Model):
    karma = models.IntegerField(default=0)
    last_access = models.DateTimeField(null=True)
    streak = models.PositiveSmallIntegerField(default=0)
    tag = models.ForeignKey(Tag, related_name='links')
    title = models.CharField(max_length=255)
    url = models.URLField(max_length=255)

    def get_page_title(self):
        session = requests.Session()
        r = session.post('https://wiki.liip.ch/dologin.action', data={
            'login': 'Log In',
            'os_destination': '/homepage.action',
            'os_password': '',
            'os_username': ''
        })

        bs = BeautifulSoup(session.get(self.url).text)
        assert False, bs.select('head title')[0].text
