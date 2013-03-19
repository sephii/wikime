from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from .forms import LinkForm
from .models import Link, Tag


def link(request, tag, action=None, filter=None):
    if action in ['e', 'edit']:
        return edit_link(request, tag)

    if action in ['m', 'more']:
        return more_link(request, tag, filter)

    try:
        tag = Tag.objects.get(name=tag)

        if len(tag.links.all()) == 1:
            assert False, tag.links.all()[0].get_page_title()
            return HttpResponseRedirect(tag.links[0])
    except Tag.DoesNotExist:
        return edit_link(request, tag)

    return more_link(request, tag, filter)


def edit_link(request, tag):
    if request.method == 'POST':
        form = LinkForm(request.POST)

        if form.is_valid():
            tag, created = Tag.objects.get_or_create(name=tag)
            link = Link(tag=tag, url=form.cleaned_data['url'])
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

    return render_to_response('links/link_list.html',
                              {'links': links},
                              RequestContext(request))
