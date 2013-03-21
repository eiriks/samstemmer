#!/usr/bin/python
# encoding: utf-8

from django.core.management.base import BaseCommand #, CommandError
from fylkesperspektiv.models import Personer, Voteringsresultat, Holmgang, Representanter, Votering

from datetime import datetime


class Command(BaseCommand):
    help = """Compute top word from perspn './manage.py holmgang' """
    
    # denne modulen må skrives om slik at den ikke sammenlikner to folk som ikke har vært på noen av de samme avstemningene som svært ulike 
    # de er ulike, men det er urettferdig å si at de er uenige, da de ikke har stemt det motsatte av hverandre (bare ikke vært der samtidig)

    lookup = {}
    lookup['for'] = 1
    lookup['mot'] = 2
    lookup['ikke_tilstede'] = 0

    desimaler = 2

    def compute_holmgang(self):
        """ how shall I do the current rep NOT all against all thing here..
        169 * 169 = 28.561 ->I just want tht 169 current MPs... 
        """
        # get current reps:
        current_reps = Representanter.objects.values('person').filter(dagens_representant=1)
        #print len(current_reps)
        #print current_reps              #[{'person': u'ADA'}, {'person': u'AESO'},  ...]  # len = 169 ok!
        # i nedd the person objects for latder lookup:

        personer = Personer.objects.filter(pk__in=[p['person'] for p in current_reps])

        # if I need about 100 votes to compute on, and absent-rate is about 40%, I need to query for about 200 votations, 
        #exclude unanimous stuff as of http://data.stortinget.no/upload/TekniskDokumentasjon.pdf point 4.16 & 4.13.1
        latest_200_votation = Votering.objects.all().values('votering_id').order_by('-votering_tid').exclude(votering_resultat_type_tekst='Enstemmig vedtatt')[:200]
        #print latest_200_votation   # [{'votering_id': 3224L}, {'votering_id': 3222L}, ...]

        # create large dict for all relevant votations..
        votes_results = {} # {1888:{'est':'for', 'jst':'mot', ...}, 1889: {... }}
        for vot in latest_200_votation:
            #print Voteringsresultat.objects.values('votering_avgitt','representant_id').filter(votering=vot['votering_id'])
            #values = Voteringsresultat.objects.values('representant_id', 'votering_avgitt').filter(votering=vot['votering_id'])
            # as seen here: http://stackoverflow.com/questions/4781242/django-query-results-as-associative-dict
            values = Voteringsresultat.objects.values_list('representant_id','votering_avgitt').filter(votering=vot['votering_id'])
            votes_results[vot['votering_id']] = dict(values)    # create dict of { u'EST': u'ikke_tilstede', u'JST': u'mot'}
        
        #print len(votes_results)    # 200 ok

        mp_vector = {}                                  # dict to hold vector-list for each mp
        for rep in current_reps:
            # create vector for this mp in the last 200 votations: (200v -> 200 * 169 = 33.800 rows from )
        #    print rep['person']
            if rep['person'] not in mp_vector:          # if mp not in mp-vector dict -> add it as empty list
                mp_vector[rep['person']] = []

            for vot in votes_results:
                try:
                    mp_vector[rep['person']].append(self.lookup[votes_results[vot][rep['person']]])
                except KeyError:                        # aka no vote from this MP was found in this vote (probably a sub, then?)
                    mp_vector[rep['person']].append(self.lookup['ikke_tilstede'])   # MP was NOT there... 
                except:
                    print "this should never happen. person: %s, votering: %s" % (rep['person'], vot)

        # print mp_vector
        print len(mp_vector)
        # alle mot alle
        now = datetime.now()
        materiale = "Siste 200 avstemninger i databasen, oppdatert %s" % (now.strftime("%Y %m %d %H:%M"))
        for mp in mp_vector:
            #if len(mp_vector[a]) != 200:
            #    print a, len(mp_vector[a]), mp_vector[a]

            deltager1=personer.get(pk=mp)               # resuse current_reps for deltager1 ...

            for mp2 in mp_vector:
                deltager2=personer.get(pk=mp2)          # resuse current_reps for deltager2 ...

                holmgang, created = Holmgang.objects.get_or_create(deltager1=deltager1, deltager2=deltager2)
                #print created # True if insert, false is update 
                holmgang.materiale = materiale
                # compute prosentlikhet


                #prosentlikhet = round(float(len([(i,j) for i,j in zip(mp_vector[mp],mp_vector[mp2]) if i==j])) / len(mp_vector[mp]) * 100, self.desimaler)
                # justerte ikke slik at å ikke være der samtidig ikke betyr enighet...
                # prosent = antall avstemninger der de to stemmer likt og mp1s stemme ikke er ikke_tilstede / siste200 * 100
                #                                                                                               |
                #                                                                                          burde være avtemninger der de begge var..
                
                prosentlikhet = round(float(len([(i,j) for i,j in zip(mp_vector[mp],mp_vector[mp2]) if i==j and i!=0])) / len(mp_vector[mp]) * 100, self.desimaler)

                #print [(i,j) for i,j in zip(mp_vector[mp],mp_vector[mp2]) if i==j ]
                #print [(i,j) for i,j in zip(mp_vector[mp],mp_vector[mp2]) if i==j and i != 0] # and mp was there


                holmgang.prosentlikhet = str(prosentlikhet) # funker ikke uten str i python 2.6
                holmgang.save()
                self.stdout.write('Successfully computed homgang for %s og %s, likhet: " %s "\n' % (deltager1, deltager2, holmgang.prosentlikhet))



    def handle(self, *args, **options):
        self.compute_holmgang()  # tar ikke person, bare alle mot alle som er dagens representanter..
        self.stdout.write('Successfully computed holmgang for alle \n')




