#!/usr/bin/python
# encoding: utf-8

from django.core.management.base import BaseCommand #, CommandError
from fylkesperspektiv.models import Personer, Voteringsresultat, Fylkeikhet, Partilikhet, Partier, Fylker, Representanter #, Votering

import numpy as np

from optparse import make_option


class Command(BaseCommand):
    #args = '<poll_id poll_id ...>'
    help = """Compute top word from perspn './manage.py compute_sim est eso jst'
    tfidf is slow, so compute at apropriate times... 
    to get all the first time, run "./manage.py compute_sim --all 
    """
    option_list = BaseCommand.option_list + (
    make_option('--all',
        action='store_true',
        dest='bootstrap',
        default=False,
        help='Get all insted of just a few'),
    )

    lookup = {}
    lookup['for'] = 1
    lookup['mot'] = 2
    lookup['ikke_tilstede'] = 0

    desimaler = 2

    def compute_partilikhet(self, person):
            # lage vector for denne personen
            #sql = "SELECT * FROM `fylkesperspektiv_voteringsresultat` WHERE `votering_avgitt` != 'ikke_tilstede' AND `representant_id_id` = '%s'" % (mp)
            result = Voteringsresultat.objects.select_related().filter(representant_id=person).exclude(votering_avgitt='ikke_tilstede')
            materiale = "%s avstemninger siste der %s deltok" % (len(result), person) # number of votations this rep has been in
            # alle avstemninger som denne MPen har vært med på
            aktuelle_avstemninger = []
            mp_vector = []
            for rep in result:
                aktuelle_avstemninger.append(int(rep.votering_id))
                mp_vector.append(self.lookup[rep.votering_avgitt])
            # print aktuelle_avstemninger
            # print mp_vector

            the_parties = {}
            for v in aktuelle_avstemninger:
                votes_from_this_round = Voteringsresultat.objects.values('votering_avgitt', 'representant_id__parti__id').filter(votering=v)

                d = {}
                for rep in votes_from_this_round:
                    #print rep['representant_id__parti__id'], rep['votering_avgitt']

                    if rep['representant_id__parti__id'] not in d:  # if parti not in d
                        d[rep['representant_id__parti__id']] = []   # add it

                    if self.lookup[rep['votering_avgitt']] != 0:
                        d[rep['representant_id__parti__id']].append(self.lookup[rep['votering_avgitt']])
                
                # append til vektoren for hvert parti
                for parti in d.keys():
                    if parti:
                        if parti not in the_parties:
                            the_parties[parti] = []
                        the_parties[parti].append(np.median(d[parti])) # har kan median også byttes ut med avg eller liknende
                        #print parti

            print "%s compared to the different parties: " % (person)
            for party in the_parties:
                #print round(float(len([(i,j) for i,j in zip(mp_vector,the_parties[party]) if i==j])) / len(mp_vector) * 100, desimaler), party
                # now create or update Partilikhet object:
                party_obj = Partier.objects.get(id=party)
                prosentlikhet = round(float(len([(i,j) for i,j in zip(mp_vector,the_parties[party]) if i==j])) / len(mp_vector) * 100, self.desimaler)
                # requires materiale & prosentlikhet allowed to be NULL, so that object can be created befor these values are updated
                partilikhet, created = Partilikhet.objects.get_or_create(person=person, parti=party_obj)
                # print partilikhet, created # created is True/False (True if created new object)
                partilikhet.materiale = materiale
                partilikhet.prosentlikhet = prosentlikhet
                # try:
                #     # update
                #     partilikhet = Partilikhet.objects.filter(person=person).filter(parti=party_obj)
                #     partilikhet.materiale = materiale
                #     partilikhet.prosentlikhet = round(float(len([(i,j) for i,j in zip(mp_vector,the_parties[party]) if i==j])) / len(mp_vector) * 100, desimaler)
                # except Partilikhet.DoesNotExist:
                #     # insert
                #     partilikhet = Partilikhet(person=person)
                #     partilikhet.parti = party_obj
                #     partilikhet.materiale = materiale
                #     partilikhet.prosentlikhet = round(float(len([(i,j) for i,j in zip(mp_vector,the_parties[party]) if i==j])) / len(mp_vector) * 100, desimaler)
                # else:
                #     print "this should not happen"
                partilikhet.save()  
                self.stdout.write('Successfully party sim for: " %s based on %s "\n' % (person, partilikhet.materiale))

    def compute_fylkelikhet(self, person):
        # lage vector for denne personen
        result = Voteringsresultat.objects.select_related().filter(representant_id=person).exclude(votering_avgitt='ikke_tilstede')
        materiale = "%s avstemninger siste der %s deltok" % (len(result), person) # number of votations this rep has been in
        
        aktuelle_avstemninger = []
        mp_vector = []
        for rep in result:
            aktuelle_avstemninger.append(int(rep.votering_id))
            mp_vector.append(self.lookup[rep.votering_avgitt])

        #print aktuelle_avstemninger
        #print mp_vector, len(mp_vector)

        the_counties = {}   # {'AA': [0,1,0], 'Ve': [full vector, comparable to mp_vector], ...}
        for v in aktuelle_avstemninger:
            # what all counties voted for this votation (think this is right..)
            votes_from_this_round = Voteringsresultat.objects.values('votering_avgitt', 'representant_id__fylke__id').filter(votering=v)

            d = {}  # temp dict for this votation 
            for rep in votes_from_this_round:
                #print rep
                if rep['representant_id__fylke__id'] not in d:  # if county not in d
                    d[rep['representant_id__fylke__id']] = []   # add it

                if self.lookup[rep['votering_avgitt']] != 0:    # exclude not_pressent votes (dont care baout them..)
                    d[rep['representant_id__fylke__id']].append(self.lookup[rep['votering_avgitt']])

            for county in d.keys():     # append to vector for each party
                #print county
                if county:
                    if county not in the_counties:
                        the_counties[county] = []
                    # print county, np.median(d[county]), d[county]
                    # THIS is the trick: based on the votes from each county,
                    # select a average/mean vote in this issue, and append to county list
                    the_counties[county].append(np.median(d[county])) # har kan median også byttes ut med avg eller liknende. Median er et problem ved ingen stemmer (nan) og to motstridene stemmer (1.5)

        for co in the_counties:
            fylke_obj = Fylker.objects.get(id=co)
            # prosentlikhet = rund_av(antall stemmer som er like i fylkes-vektor mot mp-vektor) delt på len...
            prosentlikhet = round(float(len([(i,j) for i,j in zip(mp_vector,the_counties[co]) if i==j])) / len(mp_vector) * 100, self.desimaler)
            #print round(float(len([(i,j) for i,j in zip(mp_vector,the_counties[co]) if i==j])) / len(mp_vector) * 100, self.desimaler), co#, co.encode("utf8")
        
            fylkelikhet, created = Fylkeikhet.objects.get_or_create(person=person, fylke=fylke_obj)
            #print created # false is update, true if insert
            fylkelikhet.materiale = materiale
            fylkelikhet.prosentlikhet = prosentlikhet
            fylkelikhet.save()
            self.stdout.write('Successfully county sim for: " %s based on %s : %s - %s"\n' % (person, fylkelikhet.materiale, fylkelikhet.fylke, fylkelikhet.prosentlikhet))



    def handle(self, *args, **options):

        if len(args)>0:                     # if there are args
            use_args = []                   # need these to be unicode
            for a in args:
                use_args.append(unicode(a))


        if options['bootstrap']:            # if we need to compute for all current reps
            #poll.delete()
            current_reps = Representanter.objects.all().filter(dagens_representant=True).values("person")
            use_args = []
            for rep in current_reps:
                use_args.append(rep['person'])      # these ARE unicode

        if len(args)>0 or options['bootstrap']:     # enten input verdier eller bootstrap... 
            for person_id in use_args:
                print person_id

                # finn personen (skal alltid finnes)
                person = Personer.objects.get(pk=person_id)
                
                self.compute_fylkelikhet(person)
                self.compute_partilikhet(person)

                self.stdout.write('Successfully computed ... for: " %s based "\n' % (person))




