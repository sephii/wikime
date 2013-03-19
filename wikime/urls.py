from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns(
    '',

    url(r'^(?P<tag>[^/]+)/(?:(?P<action>m|more|e|edit)/)?$', 'apps.links.views.link'),
    url(r'^(?P<tag>[^/]+)/(?:(?P<action>m|more|e|edit)/)?$', 'apps.links.views.link'),
    url(r'^(?P<tag>[^/]+)/(?P<filter>[^/]+)/(?:(?P<action>m|more|e|edit)/)?$',
        'apps.links.views.link'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
