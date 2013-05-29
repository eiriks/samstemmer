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

# etter endringer, kjør disse:
# ./manage.py schemamigration fylkesperspektiv --auto
# ./manage.py migrate fylkesperspektiv


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
    def __unicode__(self):
        return self.navn
    

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
    def __unicode__(self):
        return u'%s - %s' % (self.fra, self.til)

class Personer(models.Model):
    ''' 
    her prøver jeg å lage en generisk stortingsperson, denne finnes ikke i APIet, men skal fange opp folk som ikke
    er folkevalgte, men som likeledes ramler rundt å tinget (eg. varaer & ministre)
    Tabeller som dette bør reflekters i?
    - fylkesperspektiv_representanter aka                   Representanter      
    - fylkesperspektiv_dagensrepresentanter                 Dagensrepresentanter
    - fylkesperspektiv_dagensrepresentanter_komiteer        
    
    ting som har personer:
    # - fylkesperspektiv_saker ( hvorfor er det ingen saker her??? )
    - fylkesperspektiv_saker_saksordforer             <- derfor. saker må leke til Personer.
    - fylkesperspektiv_sporsmal (ref Personer på besvart av, på_vegne_av, famsatt_av_en_annen, rette_vedkommende, spørsmål fra, spørsmål til)
    - fylkesperspektiv_voteringsresultat (fre Representant (dette blir en via-via??, Person -> fast_vara_for, vara_for ))
    
    '''
    id = models.CharField(max_length=33, primary_key=True, unique=True)
    # her trenger jeg en URLvennlig SlugField av id'n, gjerne med prepopulated_fields https://docs.djangoproject.com/en/dev/ref/models/fields/#slugfield
    versjon = models.CharField(max_length=150, blank=True, null=True)       # her har jeg endra nå
    fornavn = models.CharField(max_length=150, blank=True)
    etternavn = models.CharField(max_length=150, blank=True)
    foedselsdato = models.DateTimeField(null=True, blank=True)
    doedsdato = models.DateTimeField(null=True, blank=True)
    kjoenn = models.CharField(max_length=18, blank=True)
    fylke = models.ForeignKey(Fylker, blank=True, null=True)        # ministre har ikke nødvendigvis dette
    parti = models.ForeignKey(Partier, blank=True, null=True)       # ministre har ikke nødvendigvis dette
    
    # denne skulle ha vært på Representanter, men pga unique_together der føkker auto_inc idene til relasjonene
    komiteer = models.ManyToManyField(Komiteer, through='KomiteeMedlemskap', blank=True, null=True) # kan ikke ha , on_delete=models.SET_NULL ??
    # def getFullName():
    #     return u'%s %s' % (self.fornavn, self.etternavn)

    top_words_in_questions = models.TextField(blank=True, null=True)
    top_tfidf_words_in_questions = models.TextField(blank=True, null=True)

    def get_fields(self):
        # funker ikke på datoer...
        return [(field.name, field.value_to_string(self)) for field in Personer._meta.fields]
    
    def __unicode__(self):
        return u'%s %s' % (self.fornavn, self.etternavn)

class Representanter(models.Model): # Personer
    ''' representanter er kun en kombinasjon av personer og stortingsperioder '''
    # at det opprettes en auto inc int id på denne er et problem...
    # skal jeg lage en reduntant models.CharField() med primary key true på denne tro?
    # funker det med uniqe_together?
    person = models.CharField(max_length=33) #, primary_key=True
    # nei, da kan en person kun vøre rep i en periode.. 
    #person = models.ForeignKey(Personer)
    stortingsperiode = models.ForeignKey(Stortingsperioder)
    # de neste 4 er ny løsning for dagens representanter.. 
    fast_vara_for = models.ForeignKey(Personer, blank=True, null=True, on_delete=models.SET_NULL, related_name='dagensrepresentanter_fast_vara_for')
    vara_for = models.ForeignKey(Personer, blank=True, null=True, on_delete=models.SET_NULL, related_name='dagensrepresentanter_vara_for')
    dagens_representant = models.BooleanField() # dette er helt klart en test...

    class Meta:
        unique_together = ("person", "stortingsperiode")
    def __unicode__(self):
        return u'%s %s' % (self.person, self.stortingsperiode)              # tror du jeg kan bruker self.person her?  


class KomiteeMedlemskap(models.Model):
    # prøver en detaljert kontrol over m2m tabellen, se https://docs.djangoproject.com/en/dev/topics/db/models/#intermediary-manytomany
    person = models.ForeignKey(Personer) # Representanter # kan denne gå til personer i stede? (nei..)
    komitee = models.ForeignKey(Komiteer)
    stortingsperiode = models.ForeignKey(Stortingsperioder)
    
    class Meta:
        unique_together = ("person", "komitee", "stortingsperiode")
    
    def __unicode__(self):
        return u'%s %s' % (self.person, self.komitee)

    # se her
    # - slett tabeller
    # - sync db
    # - kjør all import på nytt
    # - se til at dagensrepresentanters komiteer får riktig REFer





# class Dagensrepresentanter(models.Model):
#     ''' burde jeg ha hatt med dag her? er dette pr dag? 
#     des 2012 - jeg faser ut denne klassen totalt, og går for å legge dette som egenskaper på representanter
#     '''
#     #user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL) # <. må adde on_delete i alle , tror jeg 
#     person = models.ForeignKey(Personer, primary_key=True, related_name='dagensrepresentanter_person')              # satte denne til primary=true for å løse en floke. håper det funker...
#     fast_vara_for = models.ForeignKey(Personer, blank=True, null=True, related_name='dagensrepresentanter_fast_vara_for')
#     vara_for = models.ForeignKey(Personer, blank=True, null=True, related_name='dagensrepresentanter_vara_for')
#     komiteer = models.ManyToManyField(Komiteer)
#     # def __unicode__(self):
#     #     return u'%s %s' % (self.fornavn, self.etternavn)


class Saker(models.Model):
    id = models.IntegerField(primary_key=True)                          # denne kan ikke være auto-inc, så jeg lar den eksplisitt stå...
    versjon = models.CharField(max_length=150, blank=True)
    behandlet_sesjon_id = models.CharField(max_length=150, blank=True)
    dokumentgruppe = models.CharField(max_length=300, blank=True)
    henvisning = models.CharField(max_length=600, blank=True)
    innstilling_id = models.IntegerField(null=True, blank=True)
    komite = models.ForeignKey(Komiteer, blank=True, null=True)  #komiteid = models.CharField(max_length=150, blank=True)             #  !!!!!!!!             bør være relasjon til komiteer     
    #komitenavn = models.CharField(max_length=600, blank=True)                                                  # bør kunne fjernes
    korttittel = models.CharField(max_length=768, blank=True)
    sak_fremmet_id = models.IntegerField(null=True, blank=True)
    sist_oppdatert_dato = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=600, blank=True)
    tittel = models.TextField(blank=True)
    type = models.CharField(max_length=300, blank=True)
    emne = models.ManyToManyField(Emne)                                 # kan ha mange emner
    saksordforer = models.ManyToManyField(Personer)               # en sak kan ha flere saksordførere.    men de er ikke nødvendigvis represententer, de kan være vararer eller ministre ... 
    def __unicode__(self):
        return u'%s %s' % (self.id, self.tittel)


class Sporsmal(models.Model):
    id = models.IntegerField(primary_key=True)                              # vil ikke ha auto inc her, så lar den stå? 
    sesjonid = models.ForeignKey(Sesjoner) #
    versjon = models.CharField(max_length=60, blank=True, null=True)
    besvart_av = models.ForeignKey(Personer, related_name='sporsmal_besvart_av')                     # <- dette er ikke en person, men en stilling... ???
    besvart_av_minister_id = models.CharField(max_length=33, blank=True)            # her er pinen - ikke alle ministre er folkevalgte  !!
    besvart_av_minister_tittel = models.CharField(max_length=600, blank=True)
    besvart_dato = models.DateTimeField(null=True, blank=True) 
    besvart_pa_vegne_av = models.ForeignKey(Personer, blank=True, null=True, related_name='sporsmal_besvart_paa_vegne_av')
    besvart_pa_vegne_av_minister_id = models.CharField(max_length=33, blank=True)   # same same
    besvart_pa_vegne_av_minister_tittel = models.CharField(max_length=600, blank=True)
    datert_dato = models.DateTimeField(null=True, blank=True)
    flyttet_til = models.CharField(max_length=300, blank=True)
    fremsatt_av_annen = models.ForeignKey(Personer, blank=True, null=True, related_name='sporsmal_fremsatt_av_en_annen')               # et spørsmål kan være framsatt av en annen enn den som spør. får'n tro.
    rette_vedkommende = models.ForeignKey(Personer, blank=True, null=True, related_name='sporsmal_rette_vedkommende')
    rette_vedkommende_minister_id = models.CharField(max_length=33, blank=True, null=True)
    rette_vedkommende_minister_tittel = models.CharField(max_length=600, blank=True, null=True)
    sendt_dato = models.DateTimeField(null=True, blank=True)
    sporsmal_fra = models.ForeignKey(Personer, related_name='sporsmal_sporsmal_fra')
    sporsmal_nummer = models.IntegerField(null=True, blank=True)                    # antar dette er rekkefølgen på spørsmålene pr dag/spørretime ol.
    sporsmal_til = models.ForeignKey(Personer, related_name='sporsmal_sporsmal_til')
    sporsmal_til_minister_id = models.CharField(max_length=33, blank=True, null=True)
    sporsmal_til_minister_tittel = models.CharField(max_length=600, blank=True, null=True)
    status = models.CharField(max_length=600, blank=True)
    tittel = models.TextField(blank=True)
    type = models.CharField(max_length=300, blank=True)
    emne = models.ManyToManyField(Emne)                                     # et spørsmål ha ha flere emner. 
    
    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in Sporsmal._meta.fields]
    
    def get_absolute_url(self):
        return "/%i/" % self.id

    def __unicode__(self):
        return u'Spørsmål til %s fra %s' % (self.sporsmal_til, self.sporsmal_fra)

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
    votering_id = models.IntegerField(primary_key=True, max_length=10)      # gjør en lavere max lengde dette mer effektivt (følgefeil på stor index på voteringsresultat)
    votering_metode = models.CharField(max_length=300, blank=True)
    votering_resultat_type = models.CharField(max_length=300, blank=True)
    votering_resultat_type_tekst = models.CharField(max_length=300, blank=True)
    votering_tema = models.CharField(max_length=600, blank=True)
    votering_tid = models.DateTimeField(null=True, blank=True)
    # hvorfor er det ingen relasjon til voteringsforslag her? 
    def __unicode__(self):
        return u'%s (for %s mot %s) %s - %s' % (self.votering_id, self.antall_for, self.antall_mot, self.vedtatt, self.sak)

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
    #representant_id = models.CharField(max_length=33, primary_key=True)         # kan dette være varaer ????
    representant_id = models.ForeignKey(Personer, related_name='voteringsresultat_representant_id')
    versjon = models.CharField(max_length=150, blank=True)
    fast_vara_for = models.ForeignKey(Personer, blank=True, null=True, related_name='voteringsresultat_fast_vara_for')
    #fast_vara_for = models.CharField(max_length=33, blank=True)
    vara_for = models.ForeignKey(Personer, blank=True, related_name='voteringsresultat_vara_for', null=True)
    #vara_for = models.CharField(max_length=33, blank=True)
    votering_avgitt = models.CharField(max_length=300, blank=True)
    def __unicode__(self):
        return u'%s på %s' % (self.representant_id, self.votering_avgitt)
    class Meta:
        unique_together = ("votering", "representant_id")


class Voteringsvedtak(models.Model):
    votering = models.ForeignKey(Votering, db_column='votering_id')
    #voteringid = models.IntegerField()                                      # primary_key=True
    versjon = models.CharField(max_length=150, blank=True)
    vedtak_kode = models.CharField(max_length=300, blank=True)
    vedtak_kommentar = models.CharField(max_length=768, blank=True)
    vedtak_nummer = models.IntegerField()                                   # primary_key=True       # denne må være unik
    vedtak_referanse = models.CharField(max_length=600, blank=True)
    vedtak_tekst = models.TextField(blank=True)
    class Meta:
        unique_together = ("votering", "vedtak_nummer")



## her adder jeg nominate kjøringer og resultater 
class Wnominateanalyser(models.Model):
    dato = models.DateTimeField(auto_now_add=True)              # pørver dette..
    polarity1 = models.ForeignKey(Personer, related_name='wnominateanalyser_polarity1')
    polarity2 = models.ForeignKey(Personer, related_name='wnominateanalyser_polarity2')
    #resultat = models.ManyToManyField(Representantposisjoner)
    materiale = models.CharField(null=True, blank=True, max_length=600)
    # materiale -> 
    # Number of Legislators:   159 (9 legislators deleted)
    # Number of Votes:         318 (312 votes deleted) (of the n last votes)
    # Number of Dimensions:    2
    # Predicted Yeas:          16839 of 16864 (99.9%) predictions correct
    # Predicted Nays:          11421 of 11485 (99.4%) predictions correct

    #  In the two-dimensional model, over 99% of votes were correctly classified (99.7%), and the PRE (proportional reduction in error) is: 0.992. Both of these figures are extremely high.
    correctly_classified = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    pre = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)# proportional reduction in error) 
    


class Wnominateanalyserposisjoner(models.Model):
    x = models.DecimalField(max_digits=18, decimal_places=17, blank=True, null=True)
    y = models.DecimalField(max_digits=18, decimal_places=17, blank=True, null=True)
    representant = models.ForeignKey(Personer, related_name='wnominateanalyserposisjoner_representant') 
    analyse = models.ForeignKey(Wnominateanalyser, blank=True, null=True, related_name='wnominateanalyserposisjoner_analyse')


class Lix(models.Model):
    """LIX pr person basert på den teksten vi finner 
    - http://sv.wikipedia.org/wiki/LIX 
    - http://www.sprakrad.no/nb-NO/Toppmeny/Publikasjoner/Spraaknytt/Arkivet/2005/Spraaknytt_1-2_2005/Avisspraak/
    < 30    Mycket lättläst, barnböcker
    30 - 40 Lättläst, skönlitteratur, populärtidningar
    40 - 50 Medelsvår, normal tidningstext
    50 - 60 Svår, normalt värde för officiella texter
    > 60    Mycket svår, byråkratsvenska
    """
    person = models.ForeignKey(Personer, unique=True)
    dato = models.DateField(auto_now=True)   # when this LIX was computed
    materiale = models.CharField(max_length=300) # basert på: "35 spørsmål"
    value = models.DecimalField(max_digits=5, decimal_places=2) # 999.99 her tror jeg jeg vil begrense til to desimaler
    def __unicode__(self):
        return u'%s har lix %s etter %s, regnet den, %s. ' % (self.person, self.value, self.materiale, self.dato)
    # class Meta:
    #     unique_together = ("votering", "vedtak_nummer")

class Holmgang(models.Model):
    " alle mot alle blandt dagens representanter"
    deltager1 = models.ForeignKey(Personer, related_name='holmgang_person')
    deltager2 = models.ForeignKey(Personer, related_name='holmgang_person2')
    prosentlikhet = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True) # 10025.1
    materiale = models.CharField(max_length=300, blank=True, null=True) # eg: "35 avstemninger"
    class Meta:
        unique_together = ("deltager1", "deltager2")

class Partilikhet(models.Model):
    person = models.ForeignKey(Personer, related_name='partilikhet_person')
    parti = models.ForeignKey(Partier, related_name='partilikhet_partier')
    materiale = models.CharField(max_length=300, blank=True, null=True)      # so that object can be created before update 
    prosentlikhet = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True) # so that object can be created before update
    class Meta:
        unique_together = ("person", "parti")

class Fylkeikhet(models.Model):
    person = models.ForeignKey(Personer, related_name='fylkelikhet_person')
    fylke = models.ForeignKey(Fylker, related_name='fylkelikhet_fylke')
    materiale = models.CharField(max_length=300, blank=True, null=True)
    prosentlikhet = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    class Meta:
        unique_together = ("person", "fylke")
# LIX float, dato?, materiale
# likhet avg(parti), [person, parti, materiale, likhet]
# likhet avg(fylke), [person, fylke, materiale, likhet]


# regjering finnes ikke i APIet, men ser omtrent slik ut: 
# ref: http://data.stortinget.no/upload/Regjeringsdata_for_eksempelsiden.txt

# Statsministerinitialer,statsministerfornavn,statsministeretternavn,fradato,tildato,regjering,regjeringsparti
# KMB,Kjell Magne,Bondevik,19971017,20000317,Regjeringen Bondevik I,Krf
# KMB,Kjell Magne,Bondevik,19971017,20000317,Regjeringen Bondevik I,Sp
# KMB,Kjell Magne,Bondevik,19971017,20000317,Regjeringen Bondevik I,V
# JES,Jens,Stoltenberg,20000317,20011019,Regjeringen Stoltenberg I,A
# KMB,Kjell Magne,Bondevik,20011019,20051017,Regjeringen Bondevik II,Krf
# KMB,Kjell Magne,Bondevik,20011019,20051017,Regjeringen Bondevik II,H
# KMB,Kjell Magne,Bondevik,20011019,20051017,Regjeringen Bondevik II,V
# JES,Jens,Stoltenberg,20051017,NULL,Regjeringen Stoltenberg II,A
# JES,Jens,Stoltenberg,20051017,NULL,Regjeringen Stoltenberg II,Sv
# JES,Jens,Stoltenberg,20051017,NULL,Regjeringen Stoltenberg II,Sp

#aka, omtrentlig, utested:

# class Regjering(models.Model):
#     statsministerinitialer = models.ForeignKey(Personer, related_name='regjering_statsministerinitialer')
#     fradato = models.DateField()
#     tildato = models.DateField(blank=True, null=True)
#     regjering = models.CharField()
#     regjeringsparti = models.ForeignKey(Partier, related_name='regjering_aprti') #eller ikke nøkkel..
#     # redundant...
#     statsministerfornavn = models.CharField(max_length=300, blank=False)
#     statsministeretternavn = models.CharField(max_length=300, blank=False)

#     class Meta:
#         verbose_name = _('Regjering')
#         verbose_name_plural = _('Regjeringer')
#         unique_together = ("regjering", "regjeringsparti") 

#     def __unicode__(self):
#         return u'%s under %s' % (self.regjering, self.statsministerfornavn)        
    





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


# class DagensrepresentanterKomiteer(models.Model):
#     rep_id = models.CharField(max_length=33, primary_key=True)
#     kom_id = models.CharField(max_length=150, primary_key=True)
#     class Meta:
#         db_table = u'dagensrepresentanter_komiteer'

