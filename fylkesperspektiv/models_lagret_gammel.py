#!/usr/bin/python
# encoding: utf-8

# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models

class Allekomiteer(models.Model):
    id = models.CharField(max_length=150, primary_key=True)
    versjon = models.CharField(max_length=150, blank=True)
    navn = models.CharField(max_length=600)
    def __unicode__(self):
        return self.navn
    class Meta:
        db_table = u'allekomiteer'

class Allepartier(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    versjon = models.CharField(max_length=150, blank=True)
    navn = models.CharField(max_length=300)
    def __unicode__(self):
        return self.navn
    class Meta:
        db_table = u'allepartier'

class Fylker(models.Model):
    id = models.CharField(max_length=6, primary_key=True)
    navn = models.CharField(max_length=300)
    def __unicode__(self):
        return self.navn
    class Meta:
        db_table = u'fylker'

class Dagensrepresentanter(models.Model):
    id = models.CharField(max_length=33, primary_key=True)
    versjon = models.CharField(max_length=150, blank=True)
    doedsdato = models.DateTimeField(null=True, blank=True)
    etternavn = models.CharField(max_length=300, blank=True)
    foedselsdato = models.DateTimeField(null=True, blank=True)
    fornavn = models.CharField(max_length=300, blank=True)
    kjoenn = models.CharField(max_length=150, blank=True)
    # fylke = models.CharField(max_length=6, blank=True)
    fylke = models.ForeignKey(Fylker, db_column='id') #, to_field='id') #, max_length=6, blank=True)      # prover dette..
    parti = models.CharField(max_length=30, blank=True)
    fast_vara_for = models.CharField(max_length=33, blank=True)
    vara_for = models.CharField(max_length=33, blank=True)
    def __unicode__(self):
        return u'%s %s' % (self.fornavn, self.etternavn)
    class Meta:
        ordering = ['etternavn']  # sette default ordering
        db_table = u'dagensrepresentanter'


class DagensrepresentanterKomiteer(models.Model):
    rep_id = models.CharField(max_length=33, primary_key=True)
    kom_id = models.CharField(max_length=150, primary_key=True)
    def __unicode__(self):
        return u'%s %s' % (self.rep_id, self.kom_id)
    class Meta:
        db_table = u'dagensrepresentanter_komiteer'


class Emne(models.Model):
   # id = models.IntegerField(primary_key=True)
    navn = models.CharField(max_length=300)
    er_hovedtema = models.CharField(max_length=150, blank=True)
    versjon = models.CharField(max_length=30, blank=True)
    hovedtema_id = models.IntegerField(null=True, blank=True)
    def __unicode__(self):
        return self.navn
    class Meta:   
        db_table = u'emne'


class KommiteerPerSesjon(models.Model):
    sesjonid = models.CharField(max_length=33, primary_key=True)
    versjon = models.CharField(max_length=60, blank=True)
    komiteid = models.CharField(max_length=150, primary_key=True)
    komitenavn = models.CharField(max_length=600, blank=True)
    def __unicode__(self):
        return u'%s %s' % (self.komitenavn, self.sesjonid)
    class Meta:
        db_table = u'kommiteer_per_sesjon'

class PartierPerSesjon(models.Model):
    versjon = models.CharField(max_length=60, blank=True)
    partiid = models.CharField(max_length=30, primary_key=True)
    partinavn = models.CharField(max_length=300, blank=True)
    sesjonid = models.CharField(max_length=150, primary_key=True)
    def __unicode__(self):
        return u'%s %s' % (self.partinavn, self.sesjonid)
    class Meta:
        db_table = u'partier_per_sesjon'

class Representanter(models.Model):
    id = models.CharField(max_length=33, primary_key=True)
    stortingsperiodeid = models.CharField(max_length=150)
    versjon = models.CharField(max_length=150, blank=True)
    doedsdato = models.DateTimeField(null=True, blank=True)
    etternavn = models.CharField(max_length=150, blank=True)
    foedselsdato = models.DateTimeField(null=True, blank=True)
    fornavn = models.CharField(max_length=150, blank=True)
    kjoenn = models.CharField(max_length=18, blank=True)
    fylke_id = models.CharField(max_length=6)
    parti_id = models.CharField(max_length=30, blank=True)
    def __unicode__(self):
        return u'%s %s' % (self.fornavn, self.etternavn)
    class Meta:
        db_table = u'representanter'

class SakEmne(models.Model):
    saksid = models.IntegerField(primary_key=True)
    emneid = models.IntegerField(primary_key=True)
    def __unicode__(self):
        return u'%s %s' % (self.saksid, self.emneid)
    class Meta:
        db_table = u'sak_emne'

class SakSaksordfoerer(models.Model):
    saksid = models.IntegerField(primary_key=True)
    saksordfoerer = models.CharField(max_length=33, primary_key=True)
    def __unicode__(self):
        return u'%s %s' % (self.saksid, self.saksordfoerer)
    class Meta:
        db_table = u'sak_saksordfoerer'

class SakVotering(models.Model):
    sak_id = models.IntegerField(primary_key=True)
    versjon = models.CharField(max_length=150, blank=True)
    alternativ_votering_id = models.IntegerField(null=True, blank=True)
    antall_for = models.IntegerField(null=True, blank=True)
    antall_ikke_tilstede = models.IntegerField(null=True, blank=True)
    antall_mot = models.IntegerField(null=True, blank=True)
    behandlingsrekkefoelge = models.IntegerField(null=True, blank=True)
    dagsorden_sak_nummer = models.IntegerField(null=True, blank=True)
    fri_votering = models.CharField(max_length=300, blank=True)
    kommentar = models.CharField(max_length=768, blank=True)
    mote_kart_nummer = models.IntegerField(null=True, blank=True)
    personlig_votering = models.CharField(max_length=300, blank=True)
    presidentid = models.CharField(max_length=33, blank=True)
    vedtatt = models.CharField(max_length=60, blank=True)
    votering_id = models.IntegerField(primary_key=True)
    votering_metode = models.CharField(max_length=300, blank=True)
    votering_resultat_type = models.CharField(max_length=300, blank=True)
    votering_resultat_type_tekst = models.CharField(max_length=300, blank=True)
    votering_tema = models.CharField(max_length=600, blank=True)
    votering_tid = models.DateTimeField(null=True, blank=True)
    def __unicode__(self):
        return u'%s %s' % (self.sak_id, self.votering_id)
    class Meta:
        db_table = u'sak_votering'

class Saker(models.Model):
   # id = models.IntegerField(primary_key=True)
    versjon = models.CharField(max_length=150, blank=True)
    behandlet_sesjon_id = models.CharField(max_length=150, blank=True)
    dokumentgruppe = models.CharField(max_length=300, blank=True)
    henvisning = models.CharField(max_length=600, blank=True)
    innstilling_id = models.IntegerField(null=True, blank=True)
    komiteid = models.CharField(max_length=150, blank=True)
    komitenavn = models.CharField(max_length=600, blank=True)
    korttittel = models.CharField(max_length=768, blank=True)
    sak_fremmet_id = models.IntegerField(null=True, blank=True)
    sist_oppdatert_dato = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=600, blank=True)
    tittel = models.TextField(blank=True)
    type = models.CharField(max_length=300, blank=True)
    def __unicode__(self):
        return u'%s %s' % (self.id, self.tittel)
    class Meta:
        db_table = u'saker'

class Sesjoner(models.Model):
    id = models.CharField(max_length=150, primary_key=True)
    versjon = models.CharField(max_length=150, blank=True)
    fra = models.DateTimeField()
    til = models.DateTimeField()
    er_innevaerende = models.IntegerField(null=True, blank=True)
    def __unicode__(self):
        return self.id
    class Meta:
        db_table = u'sesjoner'

class Sporsmal(models.Model):
    # django vil ikke ha denne # id = models.IntegerField(primary_key=True)
    sesjonid = models.CharField(max_length=150, blank=True)
    versjon = models.CharField(max_length=60, blank=True)
    besvart_av = models.CharField(max_length=33, blank=True)
    besvart_av_minister_id = models.CharField(max_length=33, blank=True)
    besvart_av_minister_tittel = models.CharField(max_length=600, blank=True)
    besvart_dato = models.DateTimeField(null=True, blank=True)
    pa_vegne_av = models.CharField(max_length=300, blank=True)
    besvart_pa_vegne_av_minister_id = models.CharField(max_length=33, blank=True)
    besvart_pa_vegne_av_minister_tittel = models.CharField(max_length=600, blank=True)
    datert_dato = models.DateTimeField(null=True, blank=True)
    flyttet_til = models.CharField(max_length=300, blank=True)
    fremsatt_av_annen = models.CharField(max_length=33, blank=True)
    rette_vedkommende = models.CharField(max_length=33, blank=True)
    rette_vedkommende_minister_id = models.CharField(max_length=33, blank=True)
    rette_vedkommende_minister_tittel = models.CharField(max_length=600, blank=True)
    sendt_dato = models.DateTimeField(null=True, blank=True)
    sporsmal_fra = models.CharField(max_length=33, blank=True)
    sporsmal_nummer = models.IntegerField(null=True, blank=True)
    sporsmal_til = models.CharField(max_length=33, blank=True)
    sporsmal_til_minister_id = models.CharField(max_length=33, blank=True)
    sporsmal_til_minister_tittel = models.CharField(max_length=600, blank=True)
    status = models.CharField(max_length=600, blank=True)
    tittel = models.TextField(blank=True)
    type = models.CharField(max_length=300, blank=True)
    def __unicode__(self):
        return u'%s %s' % (self.id, self.tittel)
    class Meta:
        db_table = u'sporsmal'

class SporsmalEmne(models.Model):
    sporsmalid = models.IntegerField(primary_key=True)
    emneid = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'sporsmal_emne'

class Stortingsperioder(models.Model):
    id = models.CharField(max_length=150, primary_key=True)
    versjon = models.CharField(max_length=150, blank=True)
    fra = models.DateTimeField()
    til = models.DateTimeField()
    er_innevaerende = models.IntegerField(null=True, blank=True)
    def __unicode__(self):
        return u'%s %s' % (self.fra, self.til)
    class Meta:
        db_table = u'stortingsperioder'

class Voteringsforslag(models.Model):
    voteringid = models.IntegerField(primary_key=True)
    forslag_id = models.IntegerField(primary_key=True)          # naming convention is inconsistent
    versjon = models.CharField(max_length=30, blank=True)
    forslag_betegnelse = models.CharField(max_length=450, blank=True)
    forslag_betegnelse_kort = models.CharField(max_length=300, blank=True)
    forslag_levert_av_representant = models.CharField(max_length=600, blank=True)
    forslag_paa_vegne_av_tekst = models.CharField(max_length=300, blank=True)
    forslag_sorteringsnummer = models.IntegerField(null=True, blank=True)
    forslag_tekst = models.TextField(blank=True)
    forslag_type = models.CharField(max_length=300, blank=True)
    def __unicode__(self):
        return u'%s %s' % (self.fra, self.til)
    class Meta:
        db_table = u'voteringsforslag'

class Voteringsresultat(models.Model):
    voteringid = models.IntegerField(primary_key=True)
    representant_id = models.CharField(max_length=33, primary_key=True)
    versjon = models.CharField(max_length=150, blank=True)
    fast_vara_for = models.CharField(max_length=33, blank=True)
    vara_for = models.CharField(max_length=33, blank=True)
    votering = models.CharField(max_length=300, blank=True)
    def __unicode__(self):
        return u'%s %s' % (self.voteringid, self.votering)
    class Meta:
        db_table = u'voteringsresultat'

class Voteringsvedtak(models.Model):
    voteringid = models.IntegerField(primary_key=True)
    versjon = models.CharField(max_length=150, blank=True)
    vedtak_kode = models.CharField(max_length=300, blank=True)
    vedtak_kommentar = models.CharField(max_length=768, blank=True)
    vedtak_nummer = models.IntegerField(primary_key=True)
    vedtak_referanse = models.CharField(max_length=600, blank=True)
    vedtak_tekst = models.TextField(blank=True)
    def __unicode__(self):
        return u'%s %s' % (self.voteringid, self.vedtak_kode)
    class Meta:
        db_table = u'voteringsvedtak'



# ==============================================================================================
# = under her kommer en da en versjon, som da egentlig er den som ./magnate.py inspectdb lager =
# ==============================================================================================


# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models


class Fylker(models.Model):
    id = models.CharField(max_length=6, primary_key=True)
    navn = models.CharField(max_length=300)
    class Meta:
        db_table = u'fylker'


class Allekomiteer(models.Model):
    id = models.CharField(max_length=150, primary_key=True)
    versjon = models.CharField(max_length=150, blank=True)
    navn = models.CharField(max_length=600)
    class Meta:
        db_table = u'allekomiteer'

class Allepartier(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    versjon = models.CharField(max_length=150, blank=True)
    navn = models.CharField(max_length=300)
    class Meta:
        db_table = u'allepartier'

class Dagensrepresentanter(models.Model):
    id = models.CharField(max_length=33, primary_key=True)
    versjon = models.CharField(max_length=150, blank=True)
    doedsdato = models.DateTimeField(null=True, blank=True)
    etternavn = models.CharField(max_length=300, blank=True)
    foedselsdato = models.DateTimeField(null=True, blank=True)
    fornavn = models.CharField(max_length=300, blank=True)
    kjoenn = models.CharField(max_length=150, blank=True)
    #fylke = models.ForeignKey(Fylker, db_column='id')
    fylke = models.CharField(max_length=6, blank=True)
    parti = models.CharField(max_length=30, blank=True)
    fast_vara_for = models.CharField(max_length=33, blank=True)
    vara_for = models.CharField(max_length=33, blank=True)
    class Meta:
        db_table = u'dagensrepresentanter'

class DagensrepresentanterKomiteer(models.Model):
    rep_id = models.CharField(max_length=33, primary_key=True)
    kom_id = models.CharField(max_length=150, primary_key=True)
    class Meta:
        db_table = u'dagensrepresentanter_komiteer'

class Emne(models.Model):
    id = models.IntegerField(primary_key=True)
    navn = models.CharField(max_length=300)
    er_hovedtema = models.CharField(max_length=150, blank=True)
    versjon = models.CharField(max_length=30, blank=True)
    hovedtema_id = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'emne'



class KommiteerPerSesjon(models.Model):
    sesjonid = models.CharField(max_length=33, primary_key=True)
    versjon = models.CharField(max_length=60, blank=True)
    komiteid = models.CharField(max_length=150, primary_key=True)
    komitenavn = models.CharField(max_length=600, blank=True)
    class Meta:
        db_table = u'kommiteer_per_sesjon'

class PartierPerSesjon(models.Model):
    versjon = models.CharField(max_length=60, blank=True)
    partiid = models.CharField(max_length=30, primary_key=True)
    partinavn = models.CharField(max_length=300, blank=True)
    sesjonid = models.CharField(max_length=150, primary_key=True)
    class Meta:
        db_table = u'partier_per_sesjon'


class Representanter(models.Model):
    id = models.CharField(max_length=33, primary_key=True)
    stortingsperiodeid = models.CharField(max_length=150, primary_key=True)
    versjon = models.CharField(max_length=150, blank=True)
    doedsdato = models.DateTimeField(null=True, blank=True)
    etternavn = models.CharField(max_length=150, blank=True)
    foedselsdato = models.DateTimeField(null=True, blank=True)
    fornavn = models.CharField(max_length=150, blank=True)
    kjoenn = models.CharField(max_length=18, blank=True)
    fylke_id = models.CharField(max_length=6)
    parti_id = models.CharField(max_length=30, blank=True)
    class Meta:
        db_table = u'representanter'

class SakEmne(models.Model):
    saksid = models.IntegerField(primary_key=True)
    emneid = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'sak_emne'

class SakSaksordfoerer(models.Model):
    saksid = models.IntegerField(primary_key=True)
    saksordfoerer = models.CharField(max_length=33, primary_key=True)
    class Meta:
        db_table = u'sak_saksordfoerer'

class SakVotering(models.Model):
    sak_id = models.IntegerField(primary_key=True)
    versjon = models.CharField(max_length=150, blank=True)
    alternativ_votering_id = models.IntegerField(null=True, blank=True)
    antall_for = models.IntegerField(null=True, blank=True)
    antall_ikke_tilstede = models.IntegerField(null=True, blank=True)
    antall_mot = models.IntegerField(null=True, blank=True)
    behandlingsrekkefoelge = models.IntegerField(null=True, blank=True)
    dagsorden_sak_nummer = models.IntegerField(null=True, blank=True)
    fri_votering = models.CharField(max_length=300, blank=True)
    kommentar = models.CharField(max_length=768, blank=True)
    mote_kart_nummer = models.IntegerField(null=True, blank=True)
    personlig_votering = models.CharField(max_length=300, blank=True)
    presidentid = models.CharField(max_length=33, blank=True)
    vedtatt = models.CharField(max_length=60, blank=True)
    votering_id = models.IntegerField(primary_key=True)
    votering_metode = models.CharField(max_length=300, blank=True)
    votering_resultat_type = models.CharField(max_length=300, blank=True)
    votering_resultat_type_tekst = models.CharField(max_length=300, blank=True)
    votering_tema = models.CharField(max_length=600, blank=True)
    votering_tid = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = u'sak_votering'

class Saker(models.Model):
    id = models.IntegerField(primary_key=True)
    versjon = models.CharField(max_length=150, blank=True)
    behandlet_sesjon_id = models.CharField(max_length=150, blank=True)
    dokumentgruppe = models.CharField(max_length=300, blank=True)
    henvisning = models.CharField(max_length=600, blank=True)
    innstilling_id = models.IntegerField(null=True, blank=True)
    komiteid = models.CharField(max_length=150, blank=True)
    komitenavn = models.CharField(max_length=600, blank=True)
    korttittel = models.CharField(max_length=768, blank=True)
    sak_fremmet_id = models.IntegerField(null=True, blank=True)
    sist_oppdatert_dato = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=600, blank=True)
    tittel = models.TextField(blank=True)
    type = models.CharField(max_length=300, blank=True)
    class Meta:
        db_table = u'saker'

class Sesjoner(models.Model):
    id = models.CharField(max_length=150, primary_key=True)
    versjon = models.CharField(max_length=150, blank=True)
    fra = models.DateTimeField()
    til = models.DateTimeField()
    er_innevaerende = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'sesjoner'


class Sporsmal(models.Model):
    id = models.IntegerField(primary_key=True)
    sesjonid = models.CharField(max_length=150, blank=True)
    versjon = models.CharField(max_length=60, blank=True)
    besvart_av = models.CharField(max_length=33, blank=True)
    besvart_av_minister_id = models.CharField(max_length=33, blank=True)
    besvart_av_minister_tittel = models.CharField(max_length=600, blank=True)
    besvart_dato = models.DateTimeField(null=True, blank=True)
    pa_vegne_av = models.CharField(max_length=300, blank=True)
    besvart_pa_vegne_av_minister_id = models.CharField(max_length=33, blank=True)
    besvart_pa_vegne_av_minister_tittel = models.CharField(max_length=600, blank=True)
    datert_dato = models.DateTimeField(null=True, blank=True)
    flyttet_til = models.CharField(max_length=300, blank=True)
    fremsatt_av_annen = models.CharField(max_length=33, blank=True)
    rette_vedkommende = models.CharField(max_length=33, blank=True)
    rette_vedkommende_minister_id = models.CharField(max_length=33, blank=True)
    rette_vedkommende_minister_tittel = models.CharField(max_length=600, blank=True)
    sendt_dato = models.DateTimeField(null=True, blank=True)
    sporsmal_fra = models.CharField(max_length=33, blank=True)
    sporsmal_nummer = models.IntegerField(null=True, blank=True)
    sporsmal_til = models.CharField(max_length=33, blank=True)
    sporsmal_til_minister_id = models.CharField(max_length=33, blank=True)
    sporsmal_til_minister_tittel = models.CharField(max_length=600, blank=True)
    status = models.CharField(max_length=600, blank=True)
    tittel = models.TextField(blank=True)
    type = models.CharField(max_length=300, blank=True)
    class Meta:
        db_table = u'sporsmal'

class SporsmalEmne(models.Model):
    sporsmalid = models.IntegerField(primary_key=True)
    emneid = models.IntegerField(primary_key=True)
    class Meta:
        db_table = u'sporsmal_emne'

class Stortingsperioder(models.Model):
    id = models.CharField(max_length=150, primary_key=True)
    versjon = models.CharField(max_length=150, blank=True)
    fra = models.DateTimeField()
    til = models.DateTimeField()
    er_innevaerende = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'stortingsperioder'

class Voteringsforslag(models.Model):
    voteringid = models.IntegerField(primary_key=True)
    forslag_id = models.IntegerField(primary_key=True)
    versjon = models.CharField(max_length=30, blank=True)
    forslag_betegnelse = models.CharField(max_length=450, blank=True)
    forslag_betegnelse_kort = models.CharField(max_length=300, blank=True)
    forslag_levert_av_representant = models.CharField(max_length=600, blank=True)
    forslag_paa_vegne_av_tekst = models.CharField(max_length=300, blank=True)
    forslag_sorteringsnummer = models.IntegerField(null=True, blank=True)
    forslag_tekst = models.TextField(blank=True)
    forslag_type = models.CharField(max_length=300, blank=True)
    class Meta:
        db_table = u'voteringsforslag'

class Voteringsresultat(models.Model):
    voteringid = models.IntegerField(primary_key=True)
    representant_id = models.CharField(max_length=33, primary_key=True)
    versjon = models.CharField(max_length=150, blank=True)
    fast_vara_for = models.CharField(max_length=33, blank=True)
    vara_for = models.CharField(max_length=33, blank=True)
    votering = models.CharField(max_length=300, blank=True)
    class Meta:
        db_table = u'voteringsresultat'

class Voteringsvedtak(models.Model):
    voteringid = models.IntegerField(primary_key=True)
    versjon = models.CharField(max_length=150, blank=True)
    vedtak_kode = models.CharField(max_length=300, blank=True)
    vedtak_kommentar = models.CharField(max_length=768, blank=True)
    vedtak_nummer = models.IntegerField(primary_key=True)
    vedtak_referanse = models.CharField(max_length=600, blank=True)
    vedtak_tekst = models.TextField(blank=True)
    class Meta:
        db_table = u'voteringsvedtak'

# =================================================================
# = enda en ervisjon - før jeg kludrer til Person-greia for mye.  =
# =================================================================

#!/usr/bin/python
# encoding: utf-8

# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models

class Fylker(models.Model):
    id = models.CharField(max_length=6, primary_key=True)
    navn = models.CharField(max_length=300)
    def __unicode__(self):
        return self.navn
    class Meta:
        ordering = ['navn']

class Komiteer(models.Model):
    id = models.CharField(max_length=150, primary_key=True)
    versjon = models.CharField(max_length=150, blank=True)
    navn = models.CharField(max_length=600)
    def __unicode__(self):
        return self.navn

class Partier(models.Model):
    id = models.CharField(max_length=30, primary_key=True)
    versjon = models.CharField(max_length=150, blank=True)
    navn = models.CharField(max_length=300)

class Emne(models.Model):
    #id = models.IntegerField(primary_key=True)                             # disse som er int og "default" skal ut, stemmer?
    navn = models.CharField(max_length=300)
    er_hovedtema = models.CharField(max_length=150, blank=True)             # 0 hvis tema er hovedtema
    versjon = models.CharField(max_length=30, blank=True)
    hovedtema_id = models.IntegerField(null=True, blank=True)

class Sesjoner(models.Model):
    id = models.CharField(max_length=150, primary_key=True)
    versjon = models.CharField(max_length=150, blank=True)
    fra = models.DateTimeField()
    til = models.DateTimeField()
    er_innevaerende = models.IntegerField(null=True, blank=True)            # denne settes til 1 hvis dette er inneværende sesjon (de andre er 0)
    komiteer = models.ManyToManyField(Komiteer)                             # dette bør fikse en gammel manuell mange-til-mange
    parier = models.ManyToManyField(Partier)                                # dette også
    def __unicode__(self):
        return self.id

class Stortingsperioder(models.Model):
    id = models.CharField(max_length=150, primary_key=True)
    versjon = models.CharField(max_length=150, blank=True)
    fra = models.DateTimeField()
    til = models.DateTimeField()
    er_innevaerende = models.IntegerField(null=True, blank=True)            # denne settes til 1 hvis den er inneværende periode (de andre er 0)
    
class Personer(models.Model):
    ''' 
    her prøver jeg å lage en generisk stortingsperson, denne finnes ikke i APIet, men skal fange opp folk som ikke
    er folkevalgte, men som likeledes ramler rundt å tinget (eg. varaer & ministre)
    '''
    id = models.CharField(max_length=33, primary_key=True)
    versjon = models.CharField(max_length=150, blank=True)
    fornavn = models.CharField(max_length=150, blank=True)
    etternavn = models.CharField(max_length=150, blank=True)
    foedselsdato = models.DateTimeField(null=True, blank=True)
    doedsdato = models.DateTimeField(null=True, blank=True)
    kjoenn = models.CharField(max_length=18, blank=True)
    fylke = models.ForeignKey(Fylker, blank=True, null=True)        # ministre har ikke nødvendigvis dette
    parti = models.ForeignKey(Partier, blank=True, null=True)       # ministre har ikke nødvendigvis dette
    def __unicode__(self):
        return u'%s %s' % (self.fornavn, self.etternavn)

class Representanter(models.Model):
    id = models.CharField(max_length=33, primary_key=True)
    fornavn = models.CharField(max_length=150, blank=True)
    etternavn = models.CharField(max_length=150, blank=True)
    stortingsperiode = models.ForeignKey(Stortingsperioder)                       # en helt vanlig fremmednøkkel...
    #stortingsperiodeid = models.CharField(max_length=150, primary_key=True)     # denne er en kombinasjonsnøkkel - lurer på hvordan det funker...
    versjon = models.CharField(max_length=150, blank=True)
    foedselsdato = models.DateTimeField(null=True, blank=True)
    doedsdato = models.DateTimeField(null=True, blank=True)
    kjoenn = models.CharField(max_length=18, blank=True)
    fylke = models.ForeignKey(Fylker, blank=True, null=True)
    parti = models.ForeignKey(Partier)
    def __unicode__(self):
        return u'%s %s' % (self.fornavn, self.etternavn)



class Dagensrepresentanter(models.Model):
    id = models.CharField(max_length=33, primary_key=True)
    versjon = models.CharField(max_length=150, blank=True)
    doedsdato = models.DateTimeField(null=True, blank=True)
    etternavn = models.CharField(max_length=300, blank=True)
    foedselsdato = models.DateTimeField(null=True, blank=True)
    fornavn = models.CharField(max_length=300, blank=True)
    kjoenn = models.CharField(max_length=150, blank=True)
    fylke = models.ForeignKey(Fylker)
    parti = models.ForeignKey(Partier)
    fast_vara_for = models.CharField(max_length=33, blank=True)
    vara_for = models.CharField(max_length=33, blank=True)
    komiteer = models.ManyToManyField(Komiteer)                             # her er an mange-til-mage (burde bli en egen tabell)
    def __unicode__(self):
        return u'%s %s' % (self.fornavn, self.etternavn)

# class DagensrepresentanterKomiteer(models.Model):
#     rep_id = models.CharField(max_length=33, primary_key=True)
#     kom_id = models.CharField(max_length=150, primary_key=True)
#     class Meta:
#         db_table = u'dagensrepresentanter_komiteer'





class Saker(models.Model):
    id = models.IntegerField(primary_key=True)                          # denne kan ikke være auto-inc, så jeg lar den eksplisitt stå...
    versjon = models.CharField(max_length=150, blank=True)
    behandlet_sesjon_id = models.CharField(max_length=150, blank=True)
    dokumentgruppe = models.CharField(max_length=300, blank=True)
    henvisning = models.CharField(max_length=600, blank=True)
    innstilling_id = models.IntegerField(null=True, blank=True)
    komiteid = models.CharField(max_length=150, blank=True)             #  !!!!!!!!             bør være relasjon til komiteer     
    komitenavn = models.CharField(max_length=600, blank=True)           # bør kunne fjernes
    korttittel = models.CharField(max_length=768, blank=True)           # bør kunne fjernes
    sak_fremmet_id = models.IntegerField(null=True, blank=True)
    sist_oppdatert_dato = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=600, blank=True)
    tittel = models.TextField(blank=True)
    type = models.CharField(max_length=300, blank=True)
    emne = models.ManyToManyField(Emne)                                 # kan ha mange emner
    saksordforer = models.ManyToManyField(Representanter)               # en sak kan ha flere saksordførere.    men de er ikke nødvendigvis represententer, de kan være vararer eller ministre ... 
    def __unicode__(self):
        return u'%s %s' % (self.it, self.tittel)


class Sporsmal(models.Model):
    id = models.IntegerField(primary_key=True)                              # vil ikke ha auto inc her, så lar den stå? 
    sesjonid = models.ForeignKey(Sesjoner)
    #sesjonid = models.CharField(max_length=150, blank=True)
    versjon = models.CharField(max_length=60, blank=True)
    besvart_av = models.CharField(max_length=33, blank=True)                        # her er pinen - disse kan referere til folk som ikke finnes som representanter
    besvart_av_minister_id = models.CharField(max_length=33, blank=True)            # her er pinen - ikke alle ministre er folkevalgte  !!
    besvart_av_minister_tittel = models.CharField(max_length=600, blank=True)
    besvart_dato = models.DateTimeField(null=True, blank=True) 
    pa_vegne_av = models.CharField(max_length=300, blank=True)                      # dette er også et problem jm minister_id
    besvart_pa_vegne_av_minister_id = models.CharField(max_length=33, blank=True)   # same same
    besvart_pa_vegne_av_minister_tittel = models.CharField(max_length=600, blank=True)
    datert_dato = models.DateTimeField(null=True, blank=True)
    flyttet_til = models.CharField(max_length=300, blank=True)
    fremsatt_av_annen = models.CharField(max_length=33, blank=True)                 # et spørsmål kan være framsatt av en annen enn den som spør. får'n tro.
    rette_vedkommende = models.CharField(max_length=33, blank=True)                 # ting som er "flytte til" rette_vedkommende: dette er reatte vedkommende.
    rette_vedkommende_minister_id = models.CharField(max_length=33, blank=True)
    rette_vedkommende_minister_tittel = models.CharField(max_length=600, blank=True)
    sendt_dato = models.DateTimeField(null=True, blank=True)
    sporsmal_fra = models.CharField(max_length=33, blank=True)
    sporsmal_nummer = models.IntegerField(null=True, blank=True)                    # antar dette er rekkefølgen på spørsmålene pr dag/spørretime ol.
    sporsmal_til = models.CharField(max_length=33, blank=True)
    sporsmal_til_minister_id = models.CharField(max_length=33, blank=True)
    sporsmal_til_minister_tittel = models.CharField(max_length=600, blank=True)
    status = models.CharField(max_length=600, blank=True)
    tittel = models.TextField(blank=True)
    type = models.CharField(max_length=300, blank=True)
    emne = models.ManyToManyField(Emne)                                     # et spørsmål ha ha flere emner. 

class Votering(models.Model):                                           # denne erstatter den krunglete navngitte sak_votering
    sak = models.ForeignKey(Saker)                                      # fremmednøkkel til saker.
    #sak_id = models.IntegerField(primary_key=True)
    versjon = models.CharField(max_length=150, blank=True)
    alternativ_votering_id = models.IntegerField(null=True, blank=True)
    antall_for = models.IntegerField(null=True, blank=True)
    antall_ikke_tilstede = models.IntegerField(null=True, blank=True)
    antall_mot = models.IntegerField(null=True, blank=True)
    behandlingsrekkefoelge = models.IntegerField(null=True, blank=True)
    dagsorden_sak_nummer = models.IntegerField(null=True, blank=True)
    fri_votering = models.CharField(max_length=300, blank=True)
    kommentar = models.CharField(max_length=768, blank=True)
    mote_kart_nummer = models.IntegerField(null=True, blank=True)
    personlig_votering = models.CharField(max_length=300, blank=True)
    presidentid = models.CharField(max_length=33, blank=True)           # jeg kunne godt å samlet presidenter noe sted... 
    vedtatt = models.CharField(max_length=60, blank=True)
    votering_id = models.IntegerField(primary_key=True)
    votering_metode = models.CharField(max_length=300, blank=True)
    votering_resultat_type = models.CharField(max_length=300, blank=True)
    votering_resultat_type_tekst = models.CharField(max_length=300, blank=True)
    votering_tema = models.CharField(max_length=600, blank=True)
    votering_tid = models.DateTimeField(null=True, blank=True)
    def __unicode__(self):
        return u'%s %s' % (self.sak, self.vedtatt)

class Voteringsforslag(models.Model):
    #voteringid = models.IntegerField(primary_key=True)                             # denne finnes også i Votering, førsøker meg på neste linje
    votering = models.ForeignKey(Votering, db_column='votering_id')                 # jeg tror det er slik en fremmednøkkel til en ikke-primærnøkkel funker.. 
    forslag_id = models.IntegerField(primary_key=True)
    versjon = models.CharField(max_length=30, blank=True)
    forslag_betegnelse = models.CharField(max_length=450, blank=True)
    forslag_betegnelse_kort = models.CharField(max_length=300, blank=True)
    forslag_levert_av_representant = models.CharField(max_length=600, blank=True)
    forslag_paa_vegne_av_tekst = models.CharField(max_length=300, blank=True)
    forslag_sorteringsnummer = models.IntegerField(null=True, blank=True)
    forslag_tekst = models.TextField(blank=True)
    forslag_type = models.CharField(max_length=300, blank=True)

class Voteringsresultat(models.Model):
    votering = models.ForeignKey(Votering, db_column='votering_id')             # samme forsøk som i Voteringsforslag
    #voteringid = models.IntegerField(primary_key=True)
    representant_id = models.CharField(max_length=33, primary_key=True)         # kan dette være varaer ????
    versjon = models.CharField(max_length=150, blank=True)
    fast_vara_for = models.CharField(max_length=33, blank=True)
    vara_for = models.CharField(max_length=33, blank=True)
    votering = models.CharField(max_length=300, blank=True)

class Voteringsvedtak(models.Model):
    voteringid = models.IntegerField()                                      # primary_key=True
    versjon = models.CharField(max_length=150, blank=True)
    vedtak_kode = models.CharField(max_length=300, blank=True)
    vedtak_kommentar = models.CharField(max_length=768, blank=True)
    vedtak_nummer = models.IntegerField()                                   # primary_key=True       # denne må være unik
    vedtak_referanse = models.CharField(max_length=600, blank=True)
    vedtak_tekst = models.TextField(blank=True)


# class SakVotering(models.Model):                      #erstattet av Votering
#     sak_id = models.IntegerField(primary_key=True)
#     versjon = models.CharField(max_length=150, blank=True)
#     alternativ_votering_id = models.IntegerField(null=True, blank=True)
#     antall_for = models.IntegerField(null=True, blank=True)
#     antall_ikke_tilstede = models.IntegerField(null=True, blank=True)
#     antall_mot = models.IntegerField(null=True, blank=True)
#     behandlingsrekkefoelge = models.IntegerField(null=True, blank=True)
#     dagsorden_sak_nummer = models.IntegerField(null=True, blank=True)
#     fri_votering = models.CharField(max_length=300, blank=True)
#     kommentar = models.CharField(max_length=768, blank=True)
#     mote_kart_nummer = models.IntegerField(null=True, blank=True)
#     personlig_votering = models.CharField(max_length=300, blank=True)
#     presidentid = models.CharField(max_length=33, blank=True)
#     vedtatt = models.CharField(max_length=60, blank=True)
#     votering_id = models.IntegerField(primary_key=True)
#     votering_metode = models.CharField(max_length=300, blank=True)
#     votering_resultat_type = models.CharField(max_length=300, blank=True)
#     votering_resultat_type_tekst = models.CharField(max_length=300, blank=True)
#     votering_tema = models.CharField(max_length=600, blank=True)
#     votering_tid = models.DateTimeField(null=True, blank=True)
#     class Meta:
#         db_table = u'sak_votering'


# class KommiteerPerSesjon(models.Model):                               # denne er nå en mange-til-mange på Sesjon
#     sesjonid = models.CharField(max_length=33, primary_key=True)
#     versjon = models.CharField(max_length=60, blank=True)
#     komiteid = models.CharField(max_length=150, primary_key=True)
#     komitenavn = models.CharField(max_length=600, blank=True)
#     class Meta:
#         db_table = u'kommiteer_per_sesjon'

# class PartierPerSesjon(models.Model):                               # denne er nå en mange-til-mange på Sesjon
#     versjon = models.CharField(max_length=60, blank=True)
#     partiid = models.CharField(max_length=30, primary_key=True)
#     partinavn = models.CharField(max_length=300, blank=True)
#     sesjonid = models.CharField(max_length=150, primary_key=True)
#     class Meta:
#        db_table = u'partier_per_sesjon'

# class SporsmalEmne(models.Model):
#     sporsmalid = models.IntegerField(primary_key=True)
#     emneid = models.IntegerField(primary_key=True)
#     class Meta:
#         db_table = u'sporsmal_emne'

# class SakEmne(models.Model):                                          # flyttet som mange-til-mange på Saker
#     saksid = models.IntegerField(primary_key=True)
#     emneid = models.IntegerField(primary_key=True)
#     class Meta:
#         db_table = u'sak_emne'

# class SakSaksordfoerer(models.Model):                                 # flyttet som mange-til-mange på Saker
#     saksid = models.IntegerField(primary_key=True)
#     saksordfoerer = models.CharField(max_length=33, primary_key=True)
#     class Meta:
#         db_table = u'sak_saksordfoerer'
