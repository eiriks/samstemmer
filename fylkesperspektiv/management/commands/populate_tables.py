#!/usr/bin/python
# encoding: utf-8

import sys
import os
import requests         # http://kennethreitz.com/requests-python-http-module.html
from bs4 import BeautifulSoup
import xml.etree.cElementTree as et
from datetime import datetime

from django.db import connection    # the sql lib

from django.core.management.base import BaseCommand #, CommandError
from fylkesperspektiv.models import Fylker, Emne, Partier, Komiteer, Sesjoner, Stortingsperioder,Personer,Representanter, KomiteeMedlemskap,Sporsmal,Saker,Votering,Voteringsresultat,Voteringsforslag,Voteringsvedtak#, Fylkeikhet, Partilikhet,  #, 

from django.core import management      # for å kunne kjøre commandoer
from optparse import make_option

import gc

class Command(BaseCommand):
    #args = '<poll_id poll_id ...>'
    help = """script to populate tables
    to get all the first time, run "./manage.py compute_sim --all
    """
    option_list = BaseCommand.option_list + (
    make_option('--all',
        action='store_true',
        dest='bootstrap',
        default=False,
        help='Get all insted of just a few'),
    )

    def get_fylker(self):
        """ get counties from data-stortinget.no """
        url = "http://data.stortinget.no/eksport/fylker"
        r = requests.get(url)  # functions: r.status_code, r.headers['content-type'], r.content
        soup = BeautifulSoup(r.content)
        counties = []
        for co in soup.find_all('fylke'):
            county = (co.id.text, co.navn.text)
            counties.append(county)

        cursor = connection.cursor() 
        cursor.executemany(""" INSERT IGNORE into """+Fylker._meta.db_table+""" (id, navn) values (%s, %s)""", counties)
        print "%s fylker inserted" % cursor.rowcount
        #commit?

    def get_emner(self):
        """ get topics from..."""
        url = "http://data.stortinget.no/eksport/emner"
        r = requests.get(url) 
        tree = et.fromstring(r.content)
        
        emne_liste = []
        for node in tree:
            #print node.tag, node.text            # førstenivå: version & emne_liste, sistnevnte kan ittereres:
            for emne in node:
                #print "hoved:", emne.tag
                hovedemne = []
                for attribute in emne:
                    # alle hovedemner             #print attribute.tag, attribute.text
                    
                    if attribute.tag != "{http://data.stortinget.no}underemne_liste":
                        hovedemne.append(attribute.text)
                    
                    #sette av hovedemne IDer slik at undertemaene kan lenkes til hovedemner
                    if attribute.tag == "{http://data.stortinget.no}id":
                        hovedemne_id = attribute.text
                    
                    if attribute.tag == "{http://data.stortinget.no}underemne_liste":
                        # appende hovedtemaer
                        #print hoved_emne #ser bra ut
                        hovedemne.append(0) #er_hovedtema (ja) ingen ID-link
                        emne_liste.append(tuple(hovedemne))
                        hovedemne = []
                        under_emne = []
                        # hvis underemne:liste finnes
                        for subtemanode in attribute:
                            # alle underemner
                            #print "\t",subtemanode.tag # aka {http://data.stortinget.no}emne
                            for subtema in subtemanode:
                                # finne subtemaene her: 
                                #print "\t\t",subtema.tag, subtema.text
                                if subtema.tag != "{http://data.stortinget.no}underemne_liste":
                                    under_emne.append(subtema.text)
                                if subtema.tag == "{http://data.stortinget.no}underemne_liste":
                                    under_emne.append(hovedemne_id) #hovedemnet som dette er et undertema for
                                    emne_liste.append(tuple(under_emne))
                                    under_emne = []

        # sett inn i db
        cursor = connection.cursor() 
        cursor.executemany(""" INSERT IGNORE into """+Emne._meta.db_table+""" (versjon, er_hovedtema, id, navn, hovedtema_id) values (%s, %s, %s, %s, %s)""", emne_liste)
        print "%s emner inserted" % cursor.rowcount
        # commit

    def get_alle_partier(self):
        url = "http://data.stortinget.no/eksport/allepartier"
        r = requests.get(url)  # functions: r.status_code, r.headers['content-type'], r.content
        soup = BeautifulSoup(r.content)
        partier = []
        for par in soup.find_all('parti'):
            partier.append( (par.versjon.text, par.id.text, par.navn.text) )

        cursor = connection.cursor() 
        cursor.executemany(""" INSERT IGNORE into """+Partier._meta.db_table+""" (versjon, id, navn) values (%s, %s, %s)""", partier)
        print "%s partier inserted" % cursor.rowcount

    def get_alle_komiteer(self):
        ''' denne ser kun ut til å hente ut alle _dagens_ komiteer, for å hente ut alle over tid trengs sesjoner...'''
        url = "http://data.stortinget.no/eksport/allekomiteer"
        r = requests.get(url)  # functions: r.status_code, r.headers['content-type'], r.content
        soup = BeautifulSoup(r.content)
        komiteer = []
        for kom in soup.find_all('komite'):
            komiteer.append( (kom.versjon.text, kom.id.text, kom.navn.text) )

        cursor = connection.cursor() 
        cursor.executemany(""" INSERT IGNORE into """+Komiteer._meta.db_table+""" (versjon, id, navn) values (%s, %s, %s)""", komiteer)
        print "%s komiteer inserted" % cursor.rowcount

    def get_sesjoner(self):
        """ get topics from..."""
        url = "http://data.stortinget.no/eksport/sesjoner"
        r = requests.get(url) 
        soup = BeautifulSoup(r.content)
#        sessions = []
        nye_sesoner = 0
        for se in soup.find_all('sesjon'):
            sesjon_obj, created = Sesjoner.objects.get_or_create(id=se.id.text,versjon=se.versjon.text,fra=self.formate_date(se.fra.text),til=self.formate_date(se.til.text))
            if created:
                nye_sesoner += 1

        current = Sesjoner.objects.get(id=soup.find('innevaerende_sesjon').id.text)
        current.er_innevaerende = 1
        current.save()
        print "Innevaerende satt for sesjon %s." % ( current)

        test_these = Sesjoner.objects.filter(er_innevaerende=1)
        for s in test_these:
            if s.id != soup.find('innevaerende_sesjon').id.text:    # some old sessjon!
                s.er_innevaerende = None                               # remove flag
                s.save()
                print "%s er ikke lenger inneværende sesjon" % (s)
        print "%s nye sesjoner funnet" % (nye_sesoner)

    def get_stortingsperioder(self):
        url = "http://data.stortinget.no/eksport/stortingsperioder"
        r = requests.get(url) 
        soup = BeautifulSoup(r.content)
        nye_persioder = 0

        for per in soup.find_all('stortingsperiode'):
            per_obj, created = Stortingsperioder.objects.get_or_create(id=per.id.text,versjon=per.versjon.text, fra=self.formate_date(per.fra.text), til=self.formate_date(per.til.text))
            if created:
                nye_persioder += 1
        
        current = Stortingsperioder.objects.get(id=soup.find('innevaerende_stortingsperiode').id.text)
        current.er_innevaerende = 1
        current.save()
        print "inneværende stortingsperiode er satt til %s" % (current)

        test_these = Stortingsperioder.objects.filter(er_innevaerende=1)
        for s in test_these:
            if s.id != soup.find('innevaerende_stortingsperiode').id.text:
                s.er_innevaerende = None
                s.save()
                print "%s er ikke lenger inneværende stortingsperiode" % (s)
        print "%s nye stortingsperioder inserted" % (nye_persioder)


    def get_representanter(self, stortingsperiodeid):
        """ """
        url = "http://data.stortinget.no/eksport/representanter?stortingsperiodeid=%s" % (stortingsperiodeid)
        r = requests.get(url)                           #print r.status_code # 200
        soup = BeautifulSoup(r.content)
        stortingsperiode_obj = Stortingsperioder.objects.get(id=stortingsperiodeid)
        nye_personer = 0
        nye_representanter = 0
        for rep in soup.find_all('representant'):        # ikke alle representanter har fylke (det er kanskje pussig, men dog.)
            try:
                fylkeid = rep.fylke.id.text
                fylke_obj = Fylker.objects.get(id=fylkeid)
            except:
                fylke_obj = None                           # None konverteres til NULL
            try:
                parti_id = rep.parti.id.text
                parti_obj = Partier.objects.get(id=parti_id)
            except:
                parti_obj = None

            # prøv person get or create
            if not Personer.objects.filter(id=rep.id.text):     # finnes ikke
                person_obj = Personer(id=rep.id.text, versjon=rep.versjon.text,
                fornavn=rep.fornavn.text, etternavn=rep.etternavn.text,
                foedselsdato=self.formate_date(rep.foedselsdato.text), doedsdato=self.formate_date(rep.doedsdato.text),
                kjoenn=rep.kjoenn.text, fylke=fylke_obj, parti=parti_obj)
                person_obj.save()
                nye_personer +=1
            else:                                               # finnes
                person_obj = Personer.objects.get(id=rep.id.text)
   
            # så sett inn som rep, kinky uten en fornuftig id, tror dette er riktig. # vara/fast vara finnes ikke her
            if not Representanter.objects.filter(person=person_obj.id, stortingsperiode=stortingsperiode_obj):
                rep_obj = Representanter(person=person_obj.id, stortingsperiode=stortingsperiode_obj)
                rep_obj.save()
                nye_representanter +=1
        
        soup.decompose() # http://stackoverflow.com/questions/11284643/python-high-memory-usage-with-beautifulsoup
        print "fant %s nye personer og %s nye representanter" % (nye_personer, nye_representanter)


    def batch_fetch_based_on_stortingsperioder(self, function_to_run, *args):
        """ auxiliary funksjon to get data based on stortingsperioder """
        cursor = connection.cursor() 
        cursor.execute("""SELECT id FROM """+Stortingsperioder._meta.db_table)
        results = cursor.fetchall()
        for result in results:
            print "periode: %s" % (result)
            function_to_run(result[0]) 

    def insert_new_person(self, id,fornavn,etternavn,foedselsdato,doedsdato,kjoenn,versjon='1.0',fylke_id=None,parti_id=None):
        ''' aux function to insert single persons to the persons table. '''
        en_person = (id,fornavn,etternavn,foedselsdato,doedsdato,kjoenn,versjon,fylke_id,parti_id)
        cursor = connection.cursor() 
        # sett inn person, om han/hun mangler
        cursor.execute(""" INSERT IGNORE into """+Personer._meta.db_table+""" (id, fornavn, etternavn, foedselsdato, doedsdato, kjoenn, versjon, fylke_id, parti_id) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)""", en_person)
        if cursor.rowcount > 0:
            print "%s new person inserted: %s %s " % (cursor.rowcount, fornavn, etternavn)
    
    def get_current_stortingsperiode(self):
        cursor = connection.cursor()
        cursor.execute(""" SELECT id FROM """+Stortingsperioder._meta.db_table+""" WHERE er_innevaerende = 1 """)
        result = cursor.fetchone()
        return result[0]


    def get_dagensrepresentanter(self):
        """ 
        """
        print "Henter dagens representanter..."
        url = "http://data.stortinget.no/eksport/dagensrepresentanter"
        r = requests.get(url)
        soup = BeautifulSoup(r.content)

        gamle_dagensrepresentanter = list(Representanter.objects.filter(dagens_representant=1).values('person','stortingsperiode'))
        gamle_dagensrepresentanter = [p['person']+"_"+p['stortingsperiode'] for p in gamle_dagensrepresentanter] # u'ADA_2005-2009'

        nye_dagensrepresentanter = []

        for rep in soup.find_all('dagensrepresentant'):            #print rep
            try:                            # hvis det er varavirksomhet på gang må jeg sikre at den noen er vara for finnes i personer-tabellen
                fast_vara_for = rep.fast_vara_for.id.text
            except:
                fast_vara_for = None        # det er ingen som er vara_for per i dag, så jeg bare gjetter på at dette vil virke hvis dette en dag skulle bli brukt (altså st noen skulle bli fast vara for noen)
            try:
                vara_for = rep.vara_for.id.text
            except:
                vara_for = None
            
            if fast_vara_for:
                if not Personer.objects.filter(id=fast_vara_for):
                    fast_vara_for_obj = Personer(id=fast_vara_for,versjon=rep.fast_vara_for.versjon.text,
                        fornavn=rep.fast_vara_for.fornavn.text,etternavn=rep.fast_vara_for.etternavn.text,
                        foedselsdato=self.formate_date(rep.fast_vara_for.foedselsdato.text),
                        doedsdato=self.formate_date(rep.fast_vara_for.doedsdato.text), kjoenn=rep.fast_vara_for.kjoenn.text)
                    fast_vara_for_obj.save()
                else:
                    fast_vara_for_obj = Personer.objects.get(id=fast_vara_for)

            if vara_for:    # her gjetter jeg på formateringen, da jeg ikke finner eksempler.
                if not Personer.objects.filter(id=vara_for):
                    vara_for_obj = Personer(id=vara_for,versjon=rep.vara_for.versjon.text,
                        fornavn=rep.vara_for.fornavn.text,etternavn=rep.vara_for.etternavn.text,
                        foedselsdato=self.formate_date(rep.vara_for.foedselsdato.text),
                        doedsdato=self.formate_date(rep.vara_for.doedsdato.text), kjoenn=rep.vara_for.kjoenn.text)
                    vara_for_obj.save()
                else:
                    vara_for_obj = Personer.objects.get(id=vara_for)

            # sjekk om represententen finnes i Personer
            if not Personer.objects.filter(id=rep.id.text):
                rep_ny_person_fylke_obj = Fylker.objects.get(id=rep.fylke.id.text)
                rep_ny_person_parti_obj = Partier.objects.get(id=rep.parti.id.text)
                rep_ny_person_obj = Personer(id=rep.id.text,fornavn=rep.fornavn.text, etternavn=rep.etternavn.text,
                    foedselsdato=self.formate_date(rep.foedselsdato.text),doedsdato=self.formate_date(rep.doedsdato.text),kjoenn=rep.kjoenn.text, 
                    fylke=rep_ny_person_fylke_obj, parti=rep_ny_person_parti_obj)
                rep_ny_person_obj.save()
                print "fant ny person %s" % (rep_ny_person_obj)
            else:
                rep_ny_person_obj = Personer.objects.get(id=rep.id.text)

            
            stortingsperiode = self.get_current_stortingsperiode()
            stortingsperiode_obj = Stortingsperioder.objects.get(id=stortingsperiode)

            # så adder vi ham som representant, det krever at vara/fast_vara allerede finnes som Personer...
            # https://docs.djangoproject.com/en/1.3/ref/models/querysets/#django.db.models.query.QuerySet.get_or_create
            rep_obj, created = Representanter.objects.get_or_create(person=rep.id.text, stortingsperiode=stortingsperiode_obj,
                  defaults={'dagens_representant': 1})
            if created:
                print "lagde ny dagensrepresentant: %s" % rep_obj

            # update info
            if fast_vara_for:
                rep_obj.fast_vara_for = fast_vara_for_obj
            if vara_for:
                rep_obj.vara_for = vara_for_obj
            rep_obj.dagens_representant = 1
            print "oppdaterte %s" % rep_obj



            if(len(rep.find_all('komite'))>0): 
                for ref in rep.find_all('komite'):
                    # adde hvis komitee ikke finnes fra før
                    kom_obj, created = Komiteer.objects.get_or_create(id=ref.id.text,versjon=ref.versjon.text,navn=ref.navn.text)
                    if created:
                        print "Fant ny komitee: %s" % (kom_obj)
                    # håndtere KomiteeMedlemskap:
                    # Det er dog Personer, ikke Representanter som har komiteemedlemskap...
                    # http://stackoverflow.com/questions/8095813/attributeerror-manyrelatedmanager-object-has-no-attribute-add-i-do-like-in
                    
                    medlemskap, created = KomiteeMedlemskap.objects.get_or_create(person=rep_ny_person_obj, komitee=kom_obj, stortingsperiode=stortingsperiode_obj)
                    medlemskap.save()                    
                    # rep_ny_person_obj.komiteer.add(kom_obj)         # så legg til personen
            rep_obj.save()
            nye_dagensrepresentanter.append(rep_obj.person+"_"+stortingsperiode) #u'ADA_2005-2009'


        #rydde opp i nye og gamle
        # print nye_dagensrepresentanter
        # print len(nye_dagensrepresentanter)
        # print "*"*50
        # print gamle_dagensrepresentanter
        # print len(gamle_dagensrepresentanter)
        # print "*"*50
        stemt_ut = set(gamle_dagensrepresentanter) - set(nye_dagensrepresentanter)
        stemt_inn = set(nye_dagensrepresentanter) - set(gamle_dagensrepresentanter)
        # if len(stemt_inn)>0:
        #     print "Nye folk:"
        #     print stemt_inn
        
        soup.decompose() # http://stackoverflow.com/questions/11284643/python-high-memory-usage-with-beautifulsoup

        for gamlis in stemt_ut:
            skal_ut = Representanter.objects.filter(person=gamlis.split("_")[0],dagens_representant=1)
            for avgang in skal_ut:
                print avgang
                avgang.dagens_representant = 0
                avgang.save()
                print "I person er nå ute av dagens representanter: %s" % (avgang)


    def batch_fetch_stuff_by_sessjon(self,function_to_run, *args):
        """ auxiliary func to get stuff by session """
        #print function_to_run, args
        cursor = connection.cursor()
        cursor.execute("""SELECT id FROM """+Sesjoner._meta.db_table)
        results = cursor.fetchall()
        nye_sporsmal_fra_liste = []
        for result in results:#[-8:]: # siste 5 mens jeg debugger...
            nye = function_to_run(result[0], args[0])
            nye_sporsmal_fra_liste.extend(nye)
        return nye_sporsmal_fra_liste

    def get_kommiteer(self, sesjonid, flag):
        """has the arg falg to comply with batch_fetch_stuff_by_sessjon's need for args"""
        url = "http://data.stortinget.no/eksport/komiteer?sesjonid=%s" % (sesjonid)
        r = requests.get(url)
        soup = BeautifulSoup(r.content)
        nye_komiteer = []
            
        for kom in soup.find_all('komite'):
            # create if missing, else get
            kom_obj, created = Komiteer.objects.get_or_create(id=kom.id.text, navn=kom.navn.text, versjon=kom.versjon.text)
            if created:
                print "La til komitee %s" % (kom_obj)
            ses_obj = Sesjoner.objects.get(id=sesjonid)
            ses_obj.komiteer.add(kom_obj)
            ses_obj.save()
            nye_komiteer.append(kom_obj)
        return nye_komiteer

    def formate_date(self, date):
        """dødsdatoer for levende personer er ulovlige datoer.. http://stackoverflow.com/questions/10263956/use-datetime-strftime-on-years-before-1900-require-year-1900"""
        try:                                # kommer normalt i dette formatet:      1893-05-04 00:00:00
            temp_date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
        except ValueError:                  # kan også komme inn som:   2012-02-07T12:40:29.687
            temp_date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f')
        temp_date = temp_date.isoformat(" ").split(".")[0]
        return temp_date

    def get_partier(self, sesjonid, flag):
        """ dette er de som er inne (aka over sperregrensen) per stortingsvalg. (tror jeg). flag pga batch-operasjon"""
        url = "http://data.stortinget.no/eksport/partier?sesjonid=%s" % (sesjonid)
        r = requests.get(url)
        soup = BeautifulSoup(r.content)
        nye_partier = []
        for parti in soup.find_all('parti'):
            parti_obj, created = Partier.objects.get_or_create(id=parti.id.text,navn=parti.navn.text)
            if created:
                print "La til parti: %s" % (parti_obj)
                nye_partier.append(parti_obj)
            ses_obj = Sesjoner.objects.get(id=sesjonid)
            ses_obj.parier.add(parti_obj)
            ses_obj.save()
        return nye_partier

    def get_sporsmal(self, sesjonid, sporsmalstype):
        #print sesjonid, sporsmalstype
        if sporsmalstype == 'skriftligesporsmal':
            url = "http://data.stortinget.no/eksport/skriftligesporsmal?sesjonid=%s" % (sesjonid)
        elif sporsmalstype == 'sporretimesporsmal':
            url = "http://data.stortinget.no/eksport/sporretimesporsmal?sesjonid=%s" % (sesjonid)
        elif sporsmalstype == 'interpellasjoner':
            url = "http://data.stortinget.no/eksport/interpellasjoner?sesjonid=%s" % (sesjonid)
        else:
            print "feil sporsmalstype, mulige er: skriftligesporsmal, sporretimesporsmal eller interpellasjoner"
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "xml")
        nye_sporsmal_fra = []
        teller = 0

        for spor in soup.find_all('sporsmal'):
            try:
                pa_vegne_av = spor.besvart_pa_vegne_av.id.text
            except:
                pa_vegne_av = None
            try:
                besvart_pa_vegne_av_minister_id = spor.besvart_pa_vegne_av_minister_id.text
            except:
                besvart_pa_vegne_av_minister_id = None
            try: 
                besvart_pa_vegne_av_minister_tittel = spor.besvart_pa_vegne_av_minister_tittel.text
            except:
                besvart_pa_vegne_av_minister_tittel = None
            try:
                rette_vedkommende = spor.rette_vedkommende.id.text
            except:
                rette_vedkommende = None 
            try:
                rette_vedkommende_minister_id = spor.rette_vedkommende_minister_id.text
            except:
                rette_vedkommende_minister_id = None 
            try:
                rette_vedkommende_minister_tittel = spor.rette_vedkommende_minister_tittel.text
            except:
                rette_vedkommende_minister_tittel = None 
            try:
                fremsatt_av_annen = spor.fremsatt_av_annen.id.text
            except:
                fremsatt_av_annen = None
            

            if spor.besvart_av.id.text:                          # besvart_av mangler fylke & parti -> dette er en fattig måte å samle inn folk på.. 
                try:
                    besvart_av_fylke = Fylker.objects.get(id=spor.besvart_av.fylke.id.text)
                except:
                    besvart_av_fylke = None
                try:
                    besvart_av_parti = Partier.objects.get(id=spor.besvart_av.parti.id.text)
                except:
                    besvart_av_parti = None
                if not Personer.objects.filter(id=spor.besvart_av.id.text):
                    besvart_av_obj = Personer(id=spor.besvart_av.id.text, versjon=spor.besvart_av.versjon.text,
                   fornavn=spor.besvart_av.fornavn.text, etternavn=spor.besvart_av.etternavn.text,
                   foedselsdato=self.formate_date(spor.besvart_av.foedselsdato.text), doedsdato=self.formate_date(spor.besvart_av.doedsdato.text),
                   kjoenn=spor.besvart_av.kjoenn.text, fylke= besvart_av_fylke, parti=besvart_av_parti)
                    print "fant ny person (besvart av): %s" % (besvart_av_obj)
                else:
                    besvart_av_obj = Personer.objects.get(id=spor.besvart_av.id.text)
                # update
                if besvart_av_fylke:
                    besvart_av_obj.fylke = besvart_av_fylke
                if besvart_av_parti:
                    besvart_av_obj.parti = besvart_av_parti
                besvart_av_obj.save()


            if spor.sporsmal_fra.id.text:
                try:
                    sporsm_fra_fylke = Fylker.objects.get(id=spor.sporsmal_fra.fylke.id.text)
                except:
                    sporsm_fra_fylke = None
                try:
                    sporsm_fra_parti = Partier.objects.get(id=spor.sporsmal_fra.parti.id.text)
                except:
                    sporsm_fra_parti = None

                if not Personer.objects.filter(id=spor.sporsmal_fra.id.text):
                    sporsmal_fra_obj = Personer(id=spor.sporsmal_fra.id.text, 
                        fornavn=spor.sporsmal_fra.fornavn.text, etternavn=spor.sporsmal_fra.etternavn.text, 
                        doedsdato=self.formate_date(spor.sporsmal_fra.doedsdato.text), foedselsdato= self.formate_date(spor.sporsmal_fra.foedselsdato.text),
                        kjoenn=spor.sporsmal_fra.kjoenn.text, fylke= sporsm_fra_fylke, parti=sporsm_fra_parti)
                    print "fant ny person (sporsmal_fra): %s" % (sporsmal_fra_obj)
                else:   #he exists
                    sporsmal_fra_obj = Personer.objects.get(id=spor.sporsmal_fra.id.text)
                # updates? 
                sporsmal_fra_obj.save()


            if spor.sporsmal_til.id.text: # folk som får spørsmål til seg, men som ikke finnes i personer er MINISTRE
                try:
                    sporsmal_til_fylke = Fylker.objects.get(id=spor.sporsmal_til.fylke.id.text)
                except:
                    sporsmal_til_fylke = None
                try:
                    sporsmal_til_parti = Partier.objects.get(id=spor.sporsmal_til.parti.id.text)
                except:
                    sporsmal_til_parti = None
                if not Personer.objects.filter(id=spor.sporsmal_til.id.text):
                    sporsmal_til_obj = Personer(id=spor.sporsmal_til.id.text,
                    fornavn=spor.sporsmal_til.fornavn.text, etternavn=spor.sporsmal_til.etternavn.text,
                    foedselsdato=self.formate_date(spor.sporsmal_til.foedselsdato.text), doedsdato=self.formate_date(spor.sporsmal_til.doedsdato.text), 
                    kjoenn=spor.sporsmal_til.kjoenn.text, fylke=sporsmal_til_fylke, parti=sporsmal_til_parti )
                    print "fant ny person (sporsmal_til): %s" % (sporsmal_til_obj)
                else:   # he exists
                    sporsmal_til_obj = Personer.objects.get(id=spor.sporsmal_til.id.text)
                # do updates? 
                sporsmal_til_obj.save()

            if fremsatt_av_annen:
                try:
                    fremsatt_av_annen_fylke = Fylker.objects.get(id=spor.fremsatt_av_annen.fylke.id.text)
                except:
                    fremsatt_av_annen_fylke = None
                try:
                    fremsatt_av_annen_parti = Partier.objects.get(id=spor.fremsatt_av_annen.parti.id.text)
                except:
                    fremsatt_av_annen_parti = None
                if not Personer.objects.filter(id=spor.fremsatt_av_annen.id.text):
                    fremsatt_av_annen_obj = Personer(id=spor.fremsatt_av_annen.id.text, 
                    fornavn=spor.fremsatt_av_annen.fornavn.text, etternavn=spor.fremsatt_av_annen.etternavn.text,
                    foedselsdato=self.formate_date(spor.fremsatt_av_annen.foedselsdato.text), doedsdato=self.formate_date(spor.fremsatt_av_annen.doedsdato.text), 
                    kjoenn=spor.fremsatt_av_annen.kjoenn.text, parti=fremsatt_av_annen_parti, fylke=fremsatt_av_annen_fylke )
                    fremsatt_av_annen_obj.save()
                    print "fant ny person (fremsatt_av_annen): %s" % (fremsatt_av_annen_obj)

                else:
                    fremsatt_av_annen_obj = Personer.objects.get(id=spor.fremsatt_av_annen.id.text)
                # update?
                #fremsatt_av_annen_obj.save()
            else:
                fremsatt_av_annen_obj = False


            if rette_vedkommende: # ikke fylke & parti
                if not Personer.objects.filter(id=spor.rette_vedkommende.id.text):
                    rette_vedkommende_obj = Personer(id=spor.rette_vedkommende.id.text, 
                        fornavn=spor.rette_vedkommende.fornavn.text, etternavn=spor.rette_vedkommende.etternavn.text, 
                        foedselsdato=self.formate_date(spor.rette_vedkommende.foedselsdato.text), doedsdato=self.formate_date(spor.rette_vedkommende.doedsdato.text), 
                        kjoenn=spor.rette_vedkommende.kjoenn.text)
                    rette_vedkommende_obj.save()
                    print "fant ny person (rette_vedkommende): %s" % (rette_vedkommende_obj)
                else:
                    rette_vedkommende_obj = Personer.objects.get(id=spor.rette_vedkommende.id.text)
            else:
                rette_vedkommende_obj = False


            if pa_vegne_av: # ikke fylke & parti
                if not Personer.objects.filter(id=spor.besvart_pa_vegne_av.id.text):
                    besvart_pa_vegne_av_obj = Personer(id=spor.besvart_pa_vegne_av.id.text, 
                        fornavn=spor.besvart_pa_vegne_av.fornavn.text, etternavn=spor.besvart_pa_vegne_av.etternavn.text, 
                        foedselsdato=self.formate_date(spor.besvart_pa_vegne_av.foedselsdato.text), doedsdato=self.formate_date(spor.besvart_pa_vegne_av.doedsdato.text), 
                        kjoenn=spor.besvart_pa_vegne_av.kjoenn.text)
                    besvart_pa_vegne_av_obj.save()
                    print "fant ny person (besvart_pa_vegne_av): %s" % (besvart_pa_vegne_av_obj)
                else:
                    besvart_pa_vegne_av_obj = Personer.objects.get(id=spor.besvart_pa_vegne_av.id.text)
                # update? 
                besvart_pa_vegne_av_obj.save()
            else:
                besvart_pa_vegne_av_obj = False


            sporsmal_id = spor.find("id", recursive=False).text
            sesjon_obj = Sesjoner.objects.get(id=sesjonid)

            # dette ser ut til å virke, selv om get_or_create failer tidvis ellers...
            spor_obj, created = Sporsmal.objects.get_or_create(id=sporsmal_id,sesjonid=sesjon_obj,
                defaults={
                'besvart_av':besvart_av_obj,
                'besvart_pa_vegne_av_minister_id':besvart_pa_vegne_av_minister_id,
                'besvart_pa_vegne_av_minister_tittel': besvart_pa_vegne_av_minister_tittel,
                'besvart_av_minister_tittel': spor.besvart_av_minister_tittel.text,
                'flyttet_til': spor.flyttet_til.text,
                'sporsmal_fra': sporsmal_fra_obj,
                'sporsmal_til': sporsmal_til_obj,
                'status': spor.status.text,
                'tittel': spor.tittel.text,
                'type': spor.type.text
                })

            if created:
                #print u"nytt %s %s" % (sporsmalstype, spor_obj)
                teller+=1
                # if person who asked the newly created question isn't in my list of new asker:
                if sporsmal_fra_obj.id not in nye_sporsmal_fra:       # append if not in list already.
                    nye_sporsmal_fra.append(sporsmal_fra_obj.id)

            # update:
            spor_obj.versjon = spor.versjon.text
            spor_obj.besvart_av = besvart_av_obj
            spor_obj.besvart_av_minister_id = spor.besvart_av_minister_id.text
            spor_obj.besvart_av_minister_tittel = spor.besvart_av_minister_tittel.text
            spor_obj.besvart_dato = self.formate_date(spor.besvart_dato.text) #spor.besvart_dato.text
            if besvart_pa_vegne_av_obj:
                spor_obj.besvart_pa_vegne_av = besvart_pa_vegne_av_obj
            spor_obj.besvart_pa_vegne_av_minister_id = besvart_pa_vegne_av_minister_id
            spor_obj.besvart_pa_vegne_av_minister_tittel = besvart_pa_vegne_av_minister_tittel
            spor_obj.datert_dato = self.formate_date(spor.datert_dato.text)
            spor_obj.flyttet_til = spor.flyttet_til.text
            if fremsatt_av_annen_obj:
                spor_obj.fremsatt_av_annen = fremsatt_av_annen_obj
            if rette_vedkommende_obj:
                spor_obj.rette_vedkommende = rette_vedkommende_obj
            spor_obj.rette_vedkommende_minister_id = rette_vedkommende_minister_id
            spor_obj.rette_vedkommende_minister_tittel = rette_vedkommende_minister_tittel
            spor_obj.sendt_dato = self.formate_date(spor.sendt_dato.text)
            spor_obj.sporsmal_fra = sporsmal_fra_obj
            spor_obj.sporsmal_nummer = spor.sporsmal_nummer.text
            spor_obj.sporsmal_til = sporsmal_til_obj
            spor_obj.sporsmal_til_minister_id = spor.sporsmal_til_minister_id.text
            spor_obj.sporsmal_til_minister_tittel = spor.sporsmal_til_minister_tittel.text
            spor_obj.status = spor.status.text
            #spor_obj.sesjonid = sesjon_obj
            #spor_obj.tittel = spor.tittel.text     # trenger ikke oppdateres?
            #spor_obj.type = spor.type.text         # trenger ikke oppdateres?

            if(len(spor.find_all('emne'))>0):
                for ref in spor.find_all('emne'):
                    emne_obj = Emne.objects.get(id=ref.id.text)
                    #print emne_obj
                    spor_obj.emne.add(emne_obj)

            spor_obj.save()
            # her...

            
            # free some memory..
            del sporsmal_fra_obj, besvart_av_obj
            del sporsmal_til_obj, fremsatt_av_annen_obj
            del rette_vedkommende_obj, besvart_pa_vegne_av_obj
            del spor_obj
            spor.decompose() # er dette en tabbe? (eller genialt..)            

        soup.decompose()    # http://stackoverflow.com/questions/11284643/python-high-memory-usage-with-beautifulsoup
        print "Ferdig med %s for sesjon %s. %s nye funnet." % (sporsmalstype, sesjonid, teller)
        return nye_sporsmal_fra



    def get_saker(self, sesjonid, flag):
        """ trenger relasjoner til tre (3) tabeller    """
        url = "http://data.stortinget.no/eksport/saker?sesjonid=%s" % (sesjonid)
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "xml")
        nye_saker = []
        teller = 0
        for sak in soup.find_all('sak'):

            try:
                komiteid = sak.komite.id.text
            except:
                komiteid = None


            # finnes saken=
            if not Saker.objects.filter(id=sak.find("id", recursive=False).text):
                # nei, lag ny
                ny_sak_obj = Saker(id=sak.find("id", recursive=False).text,versjon=sak.versjon.text,
                    behandlet_sesjon_id=sak.behandlet_sesjon_id.text,dokumentgruppe=sak.dokumentgruppe.text,
                    henvisning=sak.henvisning.text,innstilling_id=sak.innstilling_id.text,
                    korttittel=sak.korttittel.text,sak_fremmet_id=sak.sak_fremmet_id.text,
                    sist_oppdatert_dato=self.formate_date(sak.sist_oppdatert_dato.text),
                    status=sak.status.text,tittel=sak.tittel.text,type=sak.type.text)
                teller +=1
                nye_saker.append(ny_sak_obj.id)
            else:
                ny_sak_obj = Saker.objects.get(id=sak.find("id", recursive=False).text)
            
            # oppdater: 
            ny_sak_obj.status = sak.status.text
            ny_sak_obj.sist_oppdatert_dato = self.formate_date(sak.sist_oppdatert_dato.text)

            # lagre før relasjoner kan addes..: http://stackoverflow.com/questions/5541119/django-manytomanyfield-error
            ny_sak_obj.save()
            
            # emne
            if(len(sak.find_all('emne'))>0):        
                for ref in sak.find_all('emne'):                    # her HAR xml'n IDer, men jeg lag django bruke auto_inc...
                                                                    # her heter db'n her_hovedtema, mens XML'n heter er_hovedemne
                    #print ref.id.text, ref
                    # emne_obj, created = Emne.objects.get_or_create(navn=ref.navn.text,er_hovedtema=ref.er_hovedemne.text,versjon=ref.versjon.text)
                    # if created:
                    #     print "fant nytt emne: %s" % (emne_obj)


                    #prøver basert på id, selv om det ser feil ut..
                    if not Emne.objects.filter(id=ref.id.text):
                        emne_obj = Emne(id=ref.id.text,navn=ref.navn.text,er_hovedtema=ref.er_hovedemne.text,versjon=ref.versjon.text)
                    else:
                        emne_obj = Emne.objects.get(id=ref.id.text)
                    emne_obj.save()
                    ny_sak_obj.emne.add(emne_obj)

            # saksordforer       finnes som "representant" i saksordfoerer_liste
            if(len(sak.find_all('representant'))>0):            # NB: det går visst an at det ikke er noen saksordfører også... og mange.
                for ref in sak.find_all('representant'):
                    try:
                        fylke = ref.fylke.id.text
                    except:
                        fylke = None
                    try:
                        parti = ref.parti.id.text
                    except:
                        parti = None

                    if not Personer.objects.filter(id=ref.id.text):
                        saksordforer_obj = Personer(id=ref.id.text,fornavn=ref.fornavn.text,etternavn=ref.etternavn.text,
                            versjon=ref.versjon.text,foedselsdato=self.formate_date(ref.foedselsdato.text),
                            doedsdato=self.formate_date(ref.doedsdato.text),kjoenn=ref.kjoenn.text)
                    else:
                        saksordforer_obj = Personer.objects.get(id=ref.id.text)

                    if fylke:
                        saksordf_fylke_obj = Fylker.objects.get(id=ref.fylke.id.text)
                        saksordforer_obj.fylke = saksordf_fylke_obj
                    if parti:
                        saksordf_parti_obj = Partier.objects.get(id=ref.parti.id.text)
                        saksordforer_obj.parti = saksordf_parti_obj
                    saksordforer_obj.save()
                    ny_sak_obj.saksordforer.add(saksordforer_obj)

            if komiteid:
                komite_obj, created = Komiteer.objects.get_or_create(id=sak.komite.id.text,versjon=sak.komite.versjon.text,navn=sak.komite.navn.text)
                if created:
                    print "fant ny komite: %s" % (komite_obj)
                ny_sak_obj.komite=komite_obj

            ny_sak_obj.save()

        soup.decompose()    # http://stackoverflow.com/questions/11284643/python-high-memory-usage-with-beautifulsoup
        print "ferdig med å sette inn %s nye saker for sesjonen %s" % (teller, sesjonid.encode('utf8')) # hvofor må denne encodes?
        return nye_saker


    def get_voteringer(self):
        # denne bør begrenses til nyere saker... aka sist_oppdatert_dato__gt='2009-11-17 00:00:00'
        relevante_saker = Saker.objects.filter(status='behandlet', sist_oppdatert_dato__gt='2009-11-17 00:00:00')

        for s in relevante_saker:
            #print r['id']
            url = "http://data.stortinget.no/eksport/voteringer?sakid=%s" % (s.id)
            r = requests.get(url)
            soup = BeautifulSoup(r.content, "xml")
            #print r
            for vot in soup.find_all('sak_votering'):
                # satser på at denne kombinasjonen er unik, kanskje votering_id er nok?
                if not Votering.objects.filter(sak=s,votering_id=vot.votering_id.text):
                    vot_obj = Votering(sak=s, versjon=vot.versjon.text,
                        alternativ_votering_id=vot.alternativ_votering_id.text,
                        antall_for=vot.antall_for.text,
                        antall_ikke_tilstede=vot.antall_ikke_tilstede.text,
                        antall_mot=vot.antall_mot.text,
                        behandlingsrekkefoelge=vot.behandlingsrekkefoelge.text,
                        dagsorden_sak_nummer=vot.dagsorden_sak_nummer.text,
                        fri_votering=vot.fri_votering.text,
                        kommentar=vot.kommentar.text,
                        mote_kart_nummer=vot.mote_kart_nummer.text,
                        personlig_votering=vot.personlig_votering.text,
                        presidentid=vot.president.id.text,
                        vedtatt=vot.vedtatt.text,
                        votering_id=vot.votering_id.text,
                        votering_metode=vot.votering_metode.text,
                        votering_resultat_type=vot.votering_resultat_type.text,
                        votering_resultat_type_tekst=vot.votering_resultat_type_tekst.text,
                        votering_tema=vot.votering_tema.text,
                        votering_tid=self.formate_date(vot.votering_tid.text))
                    vot_obj.save()
                #else:
                    # updates? no.
                    # vot_obj = Votering.objects.get(sak=s,votering_id=vot.votering_id.text)
            soup.decompose() # http://stackoverflow.com/questions/11284643/python-high-memory-usage-with-beautifulsoup

    def get_voteringsresultat(self, quantity="new"): # new/all. all is bootstrap to populate table first time
        if quantity=="new":
            # voteringer som finnes i vot men ikke i voteringsresultat, og som ikke er enstemmig_vedtatt
            voteringer = Votering.objects.exclude(votering_id__in=Voteringsresultat.objects.all().values('votering')).exclude(votering_resultat_type='enstemmig_vedtatt')
        else:
            voteringer = Votering.objects.all()
        print len(voteringer)
        # sys.exit()
        teller = 0
        personer_med_nye_voteringer = []
        for v in voteringer:
            url = "http://data.stortinget.no/eksport/voteringsresultat?VoteringId=%s" % (v.votering_id)
            #print url
            r = requests.get(url)
            soup = BeautifulSoup(r.content, "xml")
            #voteringid_fra_xml = soup.votering_id.text # den somme som v.votering_id
            
            for votr in soup.find_all("representant_voteringsresultat"):

                # finn person for votr.representant.id.text
                if not Personer.objects.filter(id=votr.representant.id.text):
                    representant_obj = Personer(id=votr.representant.id.text,versjon=votr.representant.versjon.text,
                        fornavn=votr.representant.fornavn.text, etternavn=votr.representant.etternavn.text,
                        foedselsdato=self.formate_date(votr.representant.foedselsdato.text),
                        doedsdato=self.formate_date(votr.representant.doedsdato.text),
                        kjoenn=votr.representant.kjoenn.text)
                    representant_parti_obj = Partier.objects.get(id=votr.representant.parti.id.text)
                    representant_fylke_obj = Fylker.objects.get(id=votr.representant.fylke.id.text)
                    representant_obj.parti = representant_parti_obj
                    representant_obj.fylke = representant_fylke_obj
                    representant_obj.save()
                    print "fant ny person: (representant som stemmer) %s" %representant_obj
                else:
                    representant_obj = Personer.objects.get(id=votr.representant.id.text)

                # hvis voteringsresultatet ikke finnes, lag det...
                if not Voteringsresultat.objects.filter(votering=v,representant_id=representant_obj):
                    ny_votering = Voteringsresultat(votering=v,representant_id=representant_obj,
                        versjon=votr.versjon.text,votering_avgitt=votr.votering.text)
                    teller+=1
                    # denne personen har stemt på noe nytt, må regne ut verdier for han/hun siden.
                    if representant_obj.id not in personer_med_nye_voteringer:
                        personer_med_nye_voteringer.append(representant_obj.id)
                else:
                    ny_votering = Voteringsresultat.objects.get(votering=v,representant_id=representant_obj)

                # else oppdatere? (nei, disse kommer en gang og alldri mer.. )

                # finnes vara-verdier?
                try:
                    fast_vara_for = votr.fast_vara_for.id.text
                except:
                    fast_vara_for = None

                try:
                    vara_for = votr.vara_for.id.text
                except:
                    vara_for = None

                if fast_vara_for: # det finnes en denne personen er fast vara for
                    if not Personer.objects.filter(id=votr.fast_vara_for.id.text):
                        fast_vara_for_obj = Personer(id=votr.fast_vara_for.id.text, versjon=votr.fast_vara_for.versjon.text,
                            fornavn=votr.fast_vara_for.fornavn.text, etternavn=votr.fast_vara_for.etternavn.text,
                            foedselsdato=self.formate_date(votr.fast_vara_for.foedselsdato.text),
                            doedsdato=self.formate_date(votr.fast_vara_for.doedsdato.text), kjoenn=votr.fast_vara_for.kjoenn.text)
                        fast_vara_for_obj.save()
                        print "fant ny person (fast vara for): %s" % (fast_vara_for_obj)
                    else:
                        fast_vara_for_obj = Personer.objects.get(id=votr.fast_vara_for.id.text)
                    ny_votering.fast_vara_for = fast_vara_for_obj
                    #ny_votering.save()


                if vara_for:
                    if not Personer.objects.filter(id=votr.vara_for.id.text):
                        vara_for_obj = Personer(id=votr.vara_for.id.text, versjon=votr.vara_for.versjon.text,
                            fornavn=votr.vara_for.fornavn.text, etternavn=votr.vara_for.etternavn.text,
                            foedselsdato=self.formate_date(votr.vara_for.foedselsdato.text),
                            doedsdato=self.formate_date(votr.vara_for.doedsdato.text), kjoenn=votr.vara_for.kjoenn.text)
                        vara_for_obj.save()
                        print "fant ny person (vara for): %s" % (vara_for_obj)
                    else:
                        vara_for_obj = Personer.objects.get(id=votr.vara_for.id.text)
                    ny_votering.vara_for = vara_for_obj
                    #ny_votering.save()

                # lagre denne
                #print ny_votering
                ny_votering.save()
                # free some memory..
                if fast_vara_for:
                    del fast_vara_for_obj

                if vara_for:
                    del vara_for_obj
                

                del representant_obj, ny_votering #, vara_for_obj, fast_vara_for_obj # disse finnes ikke alltid..
                votr.decompose()
                

            soup.decompose() # http://stackoverflow.com/questions/11284643/python-high-memory-usage-with-beautifulsoup
        print  "fant %s nye voteringsresultat. %s ersoner har nye voteringer" % (teller, len(personer_med_nye_voteringer))
        return personer_med_nye_voteringer

    def get_voteringsforslag(self):
        print "henter voteringsforslag:"
        voteringer = Votering.objects.all()
        for v in voteringer:
            url = "http://data.stortinget.no/eksport/voteringsforslag?voteringid=%s" % (v.votering_id)
            r = requests.get(url)
            soup = BeautifulSoup(r.content, "xml")
            # voteringid_fra_xml = soup.votering_id.text
            for votf in soup.find_all('voteringsforslag'):

                try:
                    rep_id = votf.forslag_levert_av_representant.text
                except:
                    rep_id = False

                if not Voteringsforslag.objects.filter(votering=v,forslag_id=votf.forslag_id.text):
                    vtor_forslag_obj = Voteringsforslag(votering=v, forslag_id=votf.forslag_id.text, versjon=votf.versjon.text,
                        forslag_betegnelse=votf.forslag_betegnelse.text,
                        forslag_betegnelse_kort=votf.forslag_betegnelse_kort.text,
                        forslag_paa_vegne_av_tekst=votf.forslag_paa_vegne_av_tekst.text,
                        forslag_sorteringsnummer=votf.forslag_sorteringsnummer.text,
                        forslag_tekst=votf.forslag_tekst.text,
                        forslag_type=votf.forslag_type.text)
                    
                    if rep_id:
                        if not Personer.objects.filter(id=votf.forslag_levert_av_representant.id.text):
                            #lag personer
                            rep_id_obj = Personer(id=votf.forslag_levert_av_representant.id.text,versjon=votf.forslag_levert_av_representant.versjon.text,
                                fornavn=votf.forslag_levert_av_representant.fornavn.text,
                                etternavn=votf.forslag_levert_av_representant.etternavn.text,
                                foedselsdato=self.formate_date(votf.forslag_levert_av_representant.doedsdato.text),
                                doedsdato=self.foedselsdato(votf.forslag_levert_av_representant.foedselsdato.text),
                                kjoenn=votf.forslag_levert_av_representant.kjoenn.text)
                            print "fant ny person (voteringsforslagsgiver): %s" % (rep_id_obj)
                            rep_id_obj.save()
                        else:
                            rep_id_obj = Personer.objects.get(id=votf.forslag_levert_av_representant.id.text)

                        vtor_forslag_obj.forslag_levert_av_representant = rep_id_obj.id
                    vtor_forslag_obj.save()

    def get_voteringsvedtak(self):
        print "henter voteringsvedtak: "
        voteringer = Votering.objects.all()
        teller = 0
        for v in voteringer:
            url = "http://data.stortinget.no/eksport/voteringsvedtak?voteringid=%s" % (v.votering_id)
            r = requests.get(url)
            soup = BeautifulSoup(r.content, "xml")
            #voteringid_fra_xml = soup.votering_id.text
            for votv in soup.find_all('voteringsvedtak'):
                if not Voteringsvedtak.objects.filter(votering=v, vedtak_nummer=votv.vedtak_nummer.text):
                    ny_voteringsvedtak_obj = Voteringsvedtak(votering=v, vedtak_nummer=votv.vedtak_nummer.text,
                        versjon=votv.versjon.text, vedtak_kode=votv.vedtak_kode.text,
                        vedtak_kommentar=votv.vedtak_kommentar.text,
                        vedtak_referanse=votv.vedtak_referanse.text,
                        vedtak_tekst=votv.vedtak_tekst.text)
                    ny_voteringsvedtak_obj.save()
                    teller+=1
        print "Fant %s nye voteringsvedtak" % (teller)

    def populate_empty_tables(self):
        """...her er det ikke så viktg med hva som returneres fra funksjonene, aka kalkuleringer gjøres på nytt uansett..
        for å f dette til å kjøre på en sever med lite minne måtte jeg dele dette opp ved å kommentere ut deler av listen
        og kjøre det flere ganger...
        """
        self.get_basics()
        #gc.collect()        # does this help?
        # # # data that depends on stortingsperioder
        self.batch_fetch_based_on_stortingsperioder(self.get_representanter)
        # # data based on sesjon_id
        #nye_komiteer = 
        self.batch_fetch_stuff_by_sessjon(self.get_kommiteer, 'komiteer')
        #print nye_komiteer
        #nye_partier = 
        self.batch_fetch_stuff_by_sessjon(self.get_partier, 'partier')
        #print nye_partier
        self.get_dagensrepresentanter() # trenger Personer, Representanter, Komiteer, KomiteeMedlemskap
        #gc.collect()        # does this help?
        
        # dette tar lang tid.. 
        self.batch_fetch_stuff_by_sessjon(self.get_sporsmal, 'sporretimesporsmal')
        #gc.collect()        # does this help?
        self.batch_fetch_stuff_by_sessjon(self.get_sporsmal, 'skriftligesporsmal')
        #gc.collect()        # does this help?
        self.batch_fetch_stuff_by_sessjon(self.get_sporsmal, 'interpellasjoner')
        #gc.collect()        # does this help?


        # personer_med_nye_sporsmal = self.batch_fetch_stuff_by_sessjon(self.get_sporsmal, 'sporretimesporsmal')
        # gc.collect()        # does this help?
        # personer_med_nye_sporsmal1 = self.batch_fetch_stuff_by_sessjon(self.get_sporsmal, 'skriftligesporsmal')
        # gc.collect()        # does this help?
        # personer_med_nye_sporsmal2 = self.batch_fetch_stuff_by_sessjon(self.get_sporsmal, 'interpellasjoner')
        # gc.collect()        # does this help?
        #print personer_med_nye_sporsmal, personer_med_nye_sporsmal1, personer_med_nye_sporsmal2
        #nye_saker = 
        #self.batch_fetch_stuff_by_sessjon(self.get_saker, 'saker')
        #print nye_saker
        
        #gc.collect()        # does this help?
        
        # # Krever saks-id:
        
        # fra saker som er behandlet.. og nyere enn 2007ish
        self.get_voteringer()

        #nye_voteringer = 
        print "get_voteringsresultat"
        self.get_voteringsresultat('all') #('new') # new/all all tar lang tid (kjørte ikke all her på djangoeurope-serveren, burde kanskje fikse dette..)
        #print nye_voteringer
        
        print "get_voteringsforslag"
        self.get_voteringsforslag()
        print "get_voteringsvedtak"
        self.get_voteringsvedtak()
        
        #
        # compute values
        #
        print "begynner kalkuleringer"
        management.call_command('compute_lix', bootstrap = True) # aka compute_top_words -all 
        management.call_command('compute_sim', bootstrap = True)
        management.call_command('compute_holmgang')
        
        management.call_command('compute_top_words', bootstrap = True) # aka compute_top_words -all 
        management.call_command('compute_oc')




    def get_basics(self):
        """data that does not have relations or dependencies to other entities"""
        self.get_fylker()
        self.get_emner()
        self.get_alle_partier()
        self.get_alle_komiteer()
        self.get_sesjoner()
        self.get_stortingsperioder()


    def get_current_sesjon(self):
        result = Sesjoner.objects.get(er_innevaerende = 1)
        return result.id

    def get_often(self):
        #current_stortingsperiode = self.get_current_stortingsperiode()
        sesjonid = self.get_current_sesjon()
        
        nye_sporretimesporsmal = self.get_sporsmal(sesjonid, 'sporretimesporsmal')
        del nye_sporretimesporsmal          # frigjør dette minne?
        nye_interpellasjoner = self.get_sporsmal(sesjonid, 'interpellasjoner')
        del nye_interpellasjoner            # frigjør dette minne?

        nye_skriftligesporsmal = self.get_sporsmal(sesjonid, 'skriftligesporsmal')        
        
        nye_saker = self.get_saker(sesjonid, 'saker')
        del nye_saker                       # frigjør dette minne?
        
        self.get_voteringer()       # voteringer over saker
        nye_voteringer = self.get_voteringsresultat('new') # resultatet på disse pr person. (new/all for hyppig eller første innsamling)
        # her bør det vel returneres en rekke lister...


        if len(nye_skriftligesporsmal)>0:
            print len(nye_skriftligesporsmal)
            management.call_command('compute_lix', *nye_skriftligesporsmal)
            management.call_command('compute_top_words', *nye_skriftligesporsmal) # dette kan ta litt tid..

        del nye_skriftligesporsmal # frigjør dette minne?

        if len(nye_voteringer)>0:
            management.call_command('compute_oc')
            management.call_command('compute_holmgang')
            management.call_command('compute_sim', *nye_voteringer)

        #return nye_interpellasjoner, nye_sporretimesporsmal


    def handle(self, *args, **options):
        start = datetime.now()

        # if len(args)>0:                     # if there are args
        #     use_args = []                   # need these to be unicode
        #     for a in args:
        #         use_args.append(unicode(a))

        # if options['bootstrap']:            # if we need to compute for all current reps
        #     current_reps = Representanter.objects.all().filter(dagens_representant=True).values("person")
        #     use_args = []
        #     for rep in current_reps:
        #         use_args.append(rep['person'])      # these ARE unicode
        
        if options['bootstrap']:
            print "Setter i gang innhøsting av alle typer data, og kalkulerer alle verdier:"
            self.populate_empty_tables()
        else:
            print "Kjører rutinemessig innhenting av data:"
            self.get_often()



        # # https://docs.djangoproject.com/en/dev/ref/django-admin/#running-management-commands-from-your-code
        # # http://stackoverflow.com/questions/10697133/django-admin-custom-commands-passing-a-list-of-strings-into-args
        # 
        # if len(personer_med_nye_sporsmal1) > 0:
        #     print personer_med_nye_sporsmal1
        #     management.call_command('compute_top_words',*personer_med_nye_sporsmal1)


        # TODO:
        # lag bootstrap && feq_update funksjoner
        # la det være flag på scriptet for å kjøre disse
        # la resultatet av innhøsting sette i gang comput_x-scriptene.



        
        end = datetime.now()-start
        self.stdout.write('Ferdig med innsamling av data, det tok: %s \n') % (end)




