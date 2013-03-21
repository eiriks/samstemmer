#!/usr/bin/python
# encoding: utf-8

from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('samstemmer.fylkesperspektiv.views',
    url(r'^$', 'index'),

    #url(r'^search/', include('haystack.urls')),



    # url(r'^komiteer/$', 'komiteer'),
    # url(r'^komiteer/(?P<kom_id>\w+)$', 'komiteer_detail'),

    
    url(r'^sporsmaal/(?P<format>\w+)/$','question_json'),

    #url(r'^search/', include('haystack.urls')),
    # den tar hvilket som helst ord og forventer fylke.. url(r'^(?P<fylke_id>\w+)/$', 'fylke'),                  # denne tar hvilke som helst bokstaver som akseptert input. katastrofe. 
)


#veier inn
# /parti/{V}/{person_id}
# /saker
# /dagensting <- standard viz av tinget med lenker til personer og partier
# /stemmegivning <- viz av stemmegivningen slik nominate gjør det?
# /sporsmal <- nettverksdiagram
# /kommiteer/{komitee-id}  ordsky?



# motstrøms:
# = hva er stemmer flertallet av denne rep'ns aprti, og er det i så fall konsist med dennes? =
# = er det i konflikt med fletallet av gruppen MP'n er i?
# = er det i konflikt med flertallet av avstenmingen?
# = stemme-historikk
#  
# = ordskyer på spørsmål
# = gruppe-tilhørighet


# nettverksdiagram.
# - hvem stiller spørsmål til hvem
#     - størrelsen på noden er antall spørsmål
#     - relasjoner mellom nodene er til/fra

# noe slikt? http://bl.ocks.org/1044242 
# eller slikt: http://bl.ocks.org/950642 eller http://bl.ocks.org/2883411


# kan dette brukes til spørsmål pr parti? http://bl.ocks.org/1314483


# xml-data for dokumentene? (auto-sammendrag?) ordskyer!


#folk som kanskje holder på med dette i Norge (i følge Østbye & Sjøvaag)
# = Tordal Jensen
# = Torild Aalberg - http://www2.svt.ntnu.no/ansatte/ansatt.aspx?id=683 sent mail.



# stopwords = ['i', 'og', 'det', 'er', 'p\x8c', 'til', 'som', 'en', '\x8c', '\x8c', 'for', 'av', 'at', 'har', 'med', 'de', 'den', 'han', 'om', 'et', 'fra', 'men', 'vi', 'var', 'jeg', 'du', 'der', 'seg', 'sier', 'vil', 'kan', 'ble', 'skal', 'etter', 'inn', 'den', 'han', 'om', 'fra', 'men', 'vi', 'var', 'jeg', 'seg', 'sier', 'vil', 'kan', 'ble', 'skal', 'etter', 'ogs\x8c', 's\x8c', 'ut', '\x8cr', 'n\x8c', 'dette', 'blir', 'ved', 'mot', 'hadde', 'to', 'la', 'lo', 'hun', 'over', 'ha', 'm\x8c', 'g\x8c', 'opp', 'f\x8c', 'andre', 'eller', 'bare', 'sin', 'mer', 'inn', 'f\xbfr', 'bli', 'v\xbert', 'enn', 'alle', 'noe', 'te', 'st', 'ik', 'ge', 'ri', 'da', 'ere', 've', 'is', 'ill', '..', '...', '....', 'we', 'as', 'va', 'the', 'jo', 'and', 'h.', '\xcc\xb4', 'p\x8c', 'p\\xc3\\x83\\xc2\\xa5', 'p\xcc\xb4', 'eg', 'rt']
# 
# def gen_tags(tags):
#     """ jeg må nok først filtrere ut en del stopord først 
#     url: http://snipplr.com/view.php?codeview&id=8875
#     """
#     words = {}
#     for x in (' '.join(tags)).split():
#         words[x] = 1 + words.get(x, 0)
#     return ' '.join([('<font size="%d">%s</font>'%(min(1+p*5/max(words.values()), 5), x)) for (x, p) in words.items()])


#veier inn
# /parti/{V}/{person_id}
# /saker
# /dagensting <- standard viz av tinget med lenker til personer og partier
# /stemmegivning <- viz av stemmegivningen slik nominate gjør det?
# /sporsmal <- nettverksdiagram
# /kommiteer/{komitee-id}  ordsky?

