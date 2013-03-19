import requests
from urlparse import urlparse
from django.conf import settings
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

    class Meta:
        ordering = ['-karma']

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
