#!/usr/bin/env python
# encoding: utf-8
import datetime
from haystack import indexes
from fylkesperspektiv.models import Sporsmal, Representanter, Fylker, Personer, Voteringsresultat, Saker # Dagensrepresentanter


class SporsmalIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True, model_attr='tittel')
    author = indexes.CharField(model_attr='sporsmal_fra')
    datert_dato = indexes.DateTimeField(model_attr='datert_dato')
    besvart_pa_vegne_av_minister_tittel = indexes.CharField(model_attr='besvart_pa_vegne_av_minister_tittel')
    
    def get_model(self):
        return Sporsmal

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(datert_dato__lte=datetime.datetime.now())



# class Sporsmal(models.Model):
#     id = models.IntegerField(primary_key=True)                              # vil ikke ha auto inc her, så lar den stå? 
#     sesjonid = models.ForeignKey(Sesjoner)
#     #sesjonid = models.CharField(max_length=150, blank=True)
#     versjon = models.CharField(max_length=60, blank=True)
#     besvart_av = models.ForeignKey(Personer, related_name='sporsmal_besvart_av')
#     #besvart_av = models.CharField(max_length=33, blank=True)                        # her er pinen - disse kan referere til folk som ikke finnes som representanter
#     #besvart_av_minister_id = models.ForeignKey(Personer)                           <- dette er ikke en person, men en stilling...
#     besvart_av_minister_id = models.CharField(max_length=33, blank=True)            # her er pinen - ikke alle ministre er folkevalgte  !!
#     besvart_av_minister_tittel = models.CharField(max_length=600, blank=True)
#     besvart_dato = models.DateTimeField(null=True, blank=True) 
#     #besvart_pa_vegne_av = models.CharField(max_length=300, blank=True)
#     besvart_pa_vegne_av = models.ForeignKey(Personer, blank=True, null=True, related_name='sporsmal_besvart_paa_vegne_av')
#     besvart_pa_vegne_av_minister_id = models.CharField(max_length=33, blank=True)   # same same
#     besvart_pa_vegne_av_minister_tittel = models.CharField(max_length=600, blank=True)
#     datert_dato = models.DateTimeField(null=True, blank=True)
#     flyttet_til = models.CharField(max_length=300, blank=True)
#     fremsatt_av_annen = models.ForeignKey(Personer, blank=True, null=True, related_name='sporsmal_fremsatt_av_en_annen')
#     #fremsatt_av_annen = models.CharField(max_length=33, blank=True)                 # et spørsmål kan være framsatt av en annen enn den som spør. får'n tro.
#     rette_vedkommende = models.ForeignKey(Personer, blank=True, null=True, related_name='sporsmal_rette_vedkommende')
#     #rette_vedkommende = models.CharField(max_length=33, blank=True)                 # ting som er "flytte til" rette_vedkommende: dette er reatte vedkommende.
#     rette_vedkommende_minister_id = models.CharField(max_length=33, blank=True, null=True)
#     rette_vedkommende_minister_tittel = models.CharField(max_length=600, blank=True, null=True)
#     sendt_dato = models.DateTimeField(null=True, blank=True)
#     sporsmal_fra = models.ForeignKey(Personer, related_name='sporsmal_sporsmal_fra')
#     #sporsmal_fra = models.CharField(max_length=33, blank=True)
#     sporsmal_nummer = models.IntegerField(null=True, blank=True)                    # antar dette er rekkefølgen på spørsmålene pr dag/spørretime ol.
#     sporsmal_til = models.ForeignKey(Personer, related_name='sporsmal_sporsmal_til')
#     #sporsmal_til = models.CharField(max_length=33, blank=True)
#     sporsmal_til_minister_id = models.CharField(max_length=33, blank=True, null=True)
#     sporsmal_til_minister_tittel = models.CharField(max_length=600, blank=True, null=True)
#     status = models.CharField(max_length=600, blank=True)
#     tittel = models.TextField(blank=True)
#     type = models.CharField(max_length=300, blank=True)
#     emne = models.ManyToManyField(Emne)     


# class Note(models.Model):
#     user = models.ForeignKey(User)
#     pub_date = models.DateTimeField()
#     title = models.CharField(max_length=200)
#     body = models.TextField()
# 
#     def __unicode__(self):
#         return self.title