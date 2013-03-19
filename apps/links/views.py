import logging
from bs4 import BeautifulSoup
from django.conf import settings
from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from .forms import LinkForm
from .models import Link, LinkGrabber, Tag

logger = logging.getLogger(__name__)


def link(request, tag, action=None, filter=None):
    if action in ['e', 'edit']:
        return edit_link(request, tag)

    if action in ['m', 'more']:
        return more_link(request, tag, filter)

    try:
        tag = Tag.objects.get(name=tag)
        tags = tag.links.all()

        if filter is not None:
            tags = tags.filter(title__icontains=filter)

        if len(tags) == 1:
            return HttpResponseRedirect(tag.links.all()[0].url)
    except Tag.DoesNotExist:
        return edit_link(request, tag)

    return more_link(request, tag.name, filter)


def edit_link(request, tag):
    if request.method == 'POST':
        form = LinkForm(request.POST)

        if form.is_valid():
            tag, created = Tag.objects.get_or_create(name=tag)
            link = Link(tag=tag, url=form.cleaned_data['url'])

            link_grabber = LinkGrabber(link.url)
            bs = BeautifulSoup(link_grabber.get())
            link.title = bs.select('head title')[0].text
            link.save()

            return HttpResponseRedirect(link.url)
    else:
        form = LinkForm()

    return render_to_response('links/link_add.html',
                              {'form': form},
                              RequestContext(request))


def more_link(request, tag, filter=None):
    try:
        tag = Tag.objects.get(name=tag)
    except Tag.DoesNotExist:
        return edit_link(request, tag)

    links = tag.links.all()

    if filter is not None:
        links = links.filter(title__icontains=filter)

    return render_to_response(
        'links/link_list.html', {
            'links': links,
        }, RequestContext(request))


def click_link(request, link_id):
    link = Link.objects.get(pk=link_id)
    logging.debug('Link #%s streak was %s, passing to %s' %
                  (link_id, link.streak, link.streak + 1))
    link.streak = min(link.streak + 1, settings.STREAK_LIMIT)
    karma_difference = fibo(link.streak)
    logging.debug('Karma difference is %s' % karma_difference)
    link.karma += karma_difference
    link.karma = min(settings.KARMA_LIMITS[1], link.karma)
    link.save()

    links_to_clean = link.tag.links.exclude(pk=link_id)
    for link_to_clean in links_to_clean:
        link_to_clean.streak = 0
        link_to_clean.karma = max(settings.KARMA_LIMITS[0],
                                  link_to_clean.karma - karma_difference)
        link_to_clean.save()

    return HttpResponse('')


def fibo(n):
    f_n_1 = 1  # F_{-1} = 1
    f_n = 0    # F_0 = 0
    for i in range(n):  # n fois
        (f_n_1, f_n) = (f_n, f_n + f_n_1)
    return f_n
