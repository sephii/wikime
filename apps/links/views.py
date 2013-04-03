import logging
from datetime import datetime
from django.http import (
    HttpResponse, HttpResponseRedirect, HttpResponseNotFound
)
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.http import require_POST
from .forms import LinkForm
from .models import Link, Tag

logger = logging.getLogger(__name__)


def link(request, tag_name, more='', filter=None):
    if more:
        return more_link(request, tag_name, filter)

    try:
        tag = Tag.objects.get(name=tag_name)
        links = tag.links.all()

        if filter is not None:
            links = links.filter(title__icontains=filter)

        if len(links) == 1:
            links[0].last_access = datetime.now()
            links[0].save()

            return HttpResponseRedirect(links[0].url)
    except Tag.DoesNotExist:
        tag = Tag(name=tag_name)
        links = tag.get_wiki_tagged_pages()

        if links:
            for url, title in links.iteritems():
                tag.add_link(url, title)

    return more_link(request, tag_name, filter)


def more_link(request, tag_name, filter=None):
    if request.method == 'POST':
        form = LinkForm(request.POST)

        if form.is_valid():
            tag, created = Tag.objects.get_or_create(name=tag_name)
            tag.add_link(form.cleaned_data['url'])

            return HttpResponseRedirect(form.cleaned_data['url'])
    else:
        form = LinkForm()

    try:
        tag = Tag.objects.get(name=tag_name)
        links = tag.get_links(filter)
    except Tag.DoesNotExist:
        tag = None
        links = []

    return render_to_response(
        'links/link_list.html', {
            'links': links,
            'form': form,
            'tag_name': tag_name,
        }, RequestContext(request))


@require_POST
def click_link(request):
    link_id = request.POST.get('id', None)

    if link_id is not None:
        link = Link.objects.get(pk=link_id)
        link.hit()
    else:
        return HttpResponseNotFound()

    return HttpResponse('')


@require_POST
def delete_link(request):
    link_id = request.POST.get('id', None)

    if link_id is not None:
        try:
            link = Link.objects.get(pk=link_id)
        except Link.DoesNotExist:
            return HttpResponseNotFound()

        tag = link.tag
        link.delete()

        if len(tag.links.all()) == 0:
            tag.delete()
    else:
        return HttpResponseNotFound()

    return HttpResponse('')
