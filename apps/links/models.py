import os
from urlparse import urlparse

from bs4 import BeautifulSoup
from confluence import ConfluenceSession
from datetime import datetime
from django.conf import settings
from django.db import models


def create_session_from_url(url):
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname

    assert hostname in settings.LINKS_WIKIS

    return ConfluenceSession(hostname, settings.LINKS_WIKIS[hostname])


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def add_link(self, link_url, link_title=None):
        if not self.id:
            self.save()

        link = Link(tag=self, url=link_url)

        if link_title is not None:
            link.title = link_title
        else:
            session = create_session_from_url(link_url)
            page = session.get_page(link_url)

            if page.headers['content-type'].startswith('text/html;'):
                bs = BeautifulSoup(page.text)

                link.title = bs.select('head title')[0].text
            else:
                parsed_url = urlparse(link_url)
                link.title = os.path.basename(parsed_url.path)

        link.save()

    def get_links(self, filter=None):
        links = self.links.all()

        if filter is not None:
            links = links.filter(title__icontains=filter)

        return links

    def get_wiki_tagged_pages(self):
        links = {}

        for hostname, auth in settings.LINKS_WIKIS.iteritems():
            pages = ConfluenceSession(hostname, auth).get_pages_with_tag(
                self.name
            )

            for link, page in pages.iteritems():
                absolute_link = 'https://{hostname}{link}'.format(
                    hostname=hostname,
                    link=link,
                )
                links[absolute_link] = page

        return links


class Link(models.Model):
    karma = models.IntegerField(default=0)
    last_access = models.DateTimeField(auto_now_add=True, null=True)
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
