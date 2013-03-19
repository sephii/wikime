from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def link_opacity(link):
    if link.karma >= 0:
        return 1

    opacity = 1 - (float(link.karma) / float(settings.KARMA_LIMITS[0]))

    return max(round(opacity, 2), 0.1)
