import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urlparse import urlparse
from django.conf import settings
from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def add_link(self, link_url):
            link_grabber = LinkGrabber(link_url)
            bs = BeautifulSoup(link_grabber.get())

            link = Link(tag=self, url=link_url)
            link.title = bs.select('head title')[0].text
            link.save()

    def get_links(self, filter=None):
        links = self.links.all()

        if filter is not None:
            links = links.filter(title__icontains=filter)

        return links


class Link(models.Model):
    karma = models.IntegerField(default=0)
    last_access = models.DateTimeField(null=True)
    combo = models.PositiveSmallIntegerField(default=0)
    tag = models.ForeignKey(Tag, related_name='links')
    title = models.CharField(max_length=255)
    url = models.URLField(max_length=255)

    class Meta:
        ordering = ['-karma', '-last_access']

    @staticmethod
    def _get_karma_for_combo(n):
        """
        That's Fibonacci.
        """
        f_n_1 = 1
        f_n = 0
        for i in range(n):
            (f_n_1, f_n) = (f_n, f_n + f_n_1)
        return f_n

    def hit(self):
        self.combo = min(self.combo + 1, settings.COMBO_LIMIT)

        karma_difference = self._get_karma_for_combo(self.combo)
        self.karma = min(self.karma + karma_difference,
                         settings.KARMA_LIMITS[1])
        self.last_access = datetime.now()
        self.save()

        links_to_clean = self.tag.links.exclude(pk=self.pk)
        for link_to_clean in links_to_clean:
            link_to_clean.combo = 0
            link_to_clean.karma = max(link_to_clean.karma - karma_difference,
                                      settings.KARMA_LIMITS[0])
            link_to_clean.save()

    def is_droppable(self):
        return self.karma <= settings.KARMA_LIMITS[0]


class LinkGrabber(object):
    def __init__(self, url):
        host = urlparse(url)
        self.hostname = host.hostname

        if (not self.hostname or self.hostname not in
                settings.LINKS_ALLOWED_HOSTS):
            raise Exception("Host '%s' is not allowed'" % self.hostname)

        self.url = url
        self.session = requests.Session()

        if self.hostname in settings.LINKS_CREDENTIALS:
            self.auth = settings.LINKS_CREDENTIALS[self.hostname]
        else:
            self.auth = None

    def _authenticate(self):
        self.session.post('https://%s/dologin.action' % self.hostname, data={
            'login': 'Log In',
            'os_destination': '/homepage.action',
            'os_username': self.auth[0],
            'os_password': self.auth[1],
        })

    def get(self):
        if self.auth is not None:
            self._authenticate()

        return self.session.get(self.url).text
