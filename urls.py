#!/usr/bin/python
# encoding: utf-8

from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('samstemmer.fylkesperspektiv.views',

    url(r'^$', 'index'),
    #url(r'^$', include('samstemmer.fylkesperspektiv.urls')),
    url(r'^lix/$','lix'),
    url(r'^person/(?P<rep_id>\w+)/$', 'person_detail'),  # [ÆØÅæøåA-Z ] denne må takle ÆØÅ eller så må noe endres.. [A_ZÆØÅ] ? .. har ikke prøvd. 
#    url(r'^person/(?P<rep_id>\w+)/$', 'person_detail'),

    url(r'^fylke/(?P<fylke_id>\w+)/$', 'fylke'),                  # denne tar hvilke som helst bokstaver som akseptert input. katastrofe. 
    url(r'^nedlastinger/$', 'nedlastinger'),
    url(r'^nedlastinger/(?P<hva>\w+)/$', 'nedlastinger2'),
    url(r'^export/', 'export'),
    #url(r'^nedlastinger', 'django.views.generic.simple.direct_to_template', {'template': 'path/to/about_us.html'}),


    url(r'^komite/(?P<kom_id>\w+)/$', 'komite'),    
    url(r'^sak/(?P<sak_id>\d+)/$', 'sak_detail'),

    url(r'^oc/$', 'oc'),
    url(r'^oc/(?P<analyse_id>\d+)/$', 'oc_detalj'),    
    url(r'^oc/data/(?P<analyse_id>\d+)/(?P<format>\w+)/$', 'oc_data'),    

    url(r'^metode/$', 'metode'),

    url(r'^sporsmaal/type_by_year/(?P<format>\w+)/$', 'question_type_by_year'), # question_type_by_year
    url(r'^sporsmaal/$', 'sporsmal'),
    url(r'^sporsmaal/(?P<sporsmal_id>\d+)/$', 'sporsmal_detail'),

    url(r'^sak/$', 'sak'),

    #url(r'^votering/$', 'fylkesperspektiv.views.votering'),
    #url(r'^avstemninger/$', 'fylkesperspektiv.views.avstemninger'),

    # http://stackoverflow.com/questions/6492952/how-can-i-pass-optional-arguments-in-django-view
    url(r'^nysgjerrigper/(?P<sesjon>\d{4}-\d+)/$', 'nysgjerrigper'),
    url(r'^nysgjerrigper/$', 'nysgjerrigper'),


    url(r'^kantgraf/$', 'sporsmal2'),
    url(r'^kantgraf/detaljer/$', 'sporsmal_detail_data'), # brukes til kantgrafen
    url(r'^kantgraf/(?P<format>\w+)/$','question_json2'),

    url(r'^finn/$', 'search'),
    # scatterplot utgår
    # url(r'^scatter/$', 'fylkesperspektiv.views.scatter'),
    # url(r'^scatter/(?P<format>\w+)/$', 'fylkesperspektiv.views.age_scatter'), # xml json

    # url(r'^polls/', include('polls.urls')),
    # url(r'^fylke/', include('fylkesperspektiv.urls')),
    # url(r'^grense/', include('boundaryservice.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    #  url(r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/path/to/media'}),
    # Examples:

    # url(r'^polls/$', 'polls.views.index'),
    # url(r'^polls/(?P<poll_id>\d+)/$', 'polls.views.detail'),
    # url(r'^polls/(?P<poll_id>\d+)/results/$', 'polls.views.results'),
    # url(r'^polls/(?P<poll_id>\d+)/vote/$', 'polls.views.vote'),
    # url(r'^$', 'index'),
)

urlpatterns += staticfiles_urlpatterns()

if settings.DEBUG:
    urlpatterns += patterns('',
            (r'^static/(.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_URL}), #settings.STATIC_PATH
    )