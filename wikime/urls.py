from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns(
    '',

    url(r'^w/out/$', 'apps.links.views.click_link'),
    url(r'^w/delete/$', 'apps.links.views.delete_link'),
    url(r'^(?P<tag_name>[^/!]+)(?P<more>!)?/$', 'apps.links.views.link'),
    url(r'^(?P<tag_name>[^/!]+)(?P<more>!)?/(?P<filter>[^/]+)/$',
        'apps.links.views.link'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
