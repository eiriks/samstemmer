#!/usr/bin/python
# encoding: utf-8

from django.core.management.base import BaseCommand #, CommandError
from fylkesperspektiv.models import Personer, Representanter, Voteringsresultat, Votering, Wnominateanalyser,Wnominateanalyserposisjoner #, Partier
# from django.db.models import Max
import math

import rpy2.robjects as robjects
import numpy as np

# import rpy2
# print rpy2.__version__

import rpy2.robjects.numpy2ri
rpy2.robjects.numpy2ri.activate()   # http://stackoverflow.com/questions/2447454/converting-python-objects-for-rpy2

# http://stackoverflow.com/questions/2447454/converting-python-objects-for-rpy2 (lengre nede)
#import rpy2.robjects as ro
#from rpy2.robjects.numpy2ri import numpy2ri
#robjects.conversion.py2ri = numpy2ri


class Command(BaseCommand):
    #args = '<poll_id poll_id ...>'
    help = """Compute OC for latest n stuff'./manage.py compute_oc est eso jst'
    uses R code:    http://voteview.com/optimal_classification.htm
    """
    # med mer enn 100 folkevalgte og voteringer > 500 er denne metoden svært presis. (p. 16)
    # også med 200 voteringer blir dette bra, men kan jeg klemme til med 500 uten
    # å bruke for mye minne på serveren? 
    # prøver: 
    number_of_votes = 500 #200   # go back this many votes to construct analysis

    lookup = {}
    lookup['for'] = 1
    lookup['mot'] = 2
    lookup['ikke_tilstede'] = 0

    # introduced by Christopher Hare Ph.D. Student and Graduate Research Assistant
    # assuably to cope with utf-8 issues
    party_codes= {}
    party_codes[u'Arbeiderpartiet'] = 100
    party_codes[u'Fremskrittspartiet'] = 200
    party_codes[u'Høyre'] = 300
    party_codes[u'Kristelig Folkeparti'] = 400
    party_codes[u'Senterpartiet'] = 500
    party_codes[u'Sosialistisk Venstreparti'] = 600
    party_codes[u'Venstre'] = 700    
    party_codes[u'Anders Langes Parti'] = 800
    party_codes[u'Bondepartiet'] = 900
    party_codes[u'Det Nye Folkepartiet'] = 1000
    party_codes[u'Framtid for Finnmark'] = 1100
    party_codes[u'Kystpartiet'] = 1200
    party_codes[u'Norges Kommunistiske Parti'] = 1300
    party_codes[u'Rød Valgallianse'] = 1400
    party_codes[u'Sosialistisk Folkeparti'] = 1500
    party_codes[u'Sosialistisk Valgforbund'] = 1600
    party_codes[u'Tverrpolitisk Folkevalgte (Kystpartiet)'] = 1700
    party_codes[u'Uavhengig representant'] = 1800


    def convert_votetext_to_numeric(self, string):
        #print string
        if string =='ikke_tilstede':
            result = 0
        elif string == 'mot':
            result = 6
        elif string == 'for':
            result = 1
        else:
            result = 9 # missing data      
        return result
    
    # def isFloat(self, string):
    #     try:
    #         float(string)
    #         return True
    #     except ValueError:
    #         return False

    def construct_dataset(self, number_of_votes):
        # get current MPs
        current_reps = Representanter.objects.values('person').filter(dagens_representant=1)
        # as list of Person objects
        personer = Personer.objects.filter(pk__in=[p['person'] for p in current_reps]) 

        person_vector = {}
        for p in personer:
            #print p, p.id
            person_vector[p.id] = [p.fornavn + u' ' + p.etternavn,p.parti.navn]

        #print person_vector

        latest_200_votation = Votering.objects.all().values('votering_id').order_by('-votering_tid').exclude(votering_resultat_type_tekst='Enstemmig vedtatt')[:number_of_votes]

        votes_results = {}      # {1888:{'est':'for', 'jst':'mot', ...}, 1889: {... }}
        missing_counter = 0     # to see how big this problem is..
        for vot in latest_200_votation:
            values = Voteringsresultat.objects.values_list('representant_id','votering_avgitt').filter(votering=vot['votering_id'])
            votes_results[vot['votering_id']] = dict(values)    # create dict of { u'EST': u'ikke_tilstede', u'JST': u'mot'}
            #print votes_results
            for mp in person_vector:
                try:
                    person_vector[mp].append(self.convert_votetext_to_numeric(votes_results[vot['votering_id']][mp]))
                except KeyError:
                    person_vector[mp].append(9)     # append 9 missing data
                    #print "KeyError person fantes ikke i den avstemningen.."
                    missing_counter+=1              # count these ocations to see size of problem
                except:
                    print "this should never happen.. person: %s - votering: %s" % (mp, vot['votering_id'])
        #print "%s missing - %s percent of votes" % (missing_counter, round(missing_counter/float(len(latest_200_votation)*len(person_vector))*100,1))
        return person_vector


    def oc(self, data):
        """lerning rpy2 from here: https://github.com/thehackerwithin/Python2010/wiki/PyBCSession08
        OC manual for r: http://cran.r-project.org/web/packages/oc/oc.pdf
        """

        # create list from data dict:
        data_list = []
        for datum in data:
            #print type(datum)
            this_item = [datum]                                             # start with id
            this_item.extend(data[datum])                                   # add vector
            this_item.insert(3, self.party_codes[data[datum][1]])           # insert party code
            data_list.append(this_item)                                     # add to data_list
        
        # write this to csv-file to test in Rstudio
        # with open('eiriks_norge_file.csv', 'w') as f:
        #     for l in data_list:
        #         f.write(", ".join(unicode(v) for v in l).encode("utf8")+"\n")


        # create np array of that list (it turnes out that np-array to rpy2 works, while python dict fails..)
        np_data_list = np.array(data_list)
        

        #print np_data_list  # er ting fortsatt i unicode?? ja: [[u'B\xc5H' u'B\xe5rd Hoksrud' u'Fremskrittspartiet' ..., u'0' u'0' u'0']
        
        # create r object in python
        r = robjects.r
        #print r.sessionInfo()

        # r code based on Christopher Hares' run-though of this data, ported here to rpy2
        r('''
        rm(list=ls(all=TRUE))    # works when before function
        calculate_oc_values <- function(data, cons1, cons2) {
            
            suppressMessages(library(MASS))
            suppressMessages(library(foreign))
            suppressMessages(library(basicspace))
            # suppressMessages(library(rgl)) # a 3D viz device needed? 
            # suppressMessages(library(effects)) # http://cran.r-project.org/web/packages/effects/
            suppressMessages(library(lattice))
            suppressMessages(library(oc))
            suppressMessages(library(wnominate))
            
            #print(Encoding(data)) # unknown ...
            
            legisname <- data[,1]
            legisname <- as.character(legisname)
            partyname <- data[,3]
            partyname <- as.character(partyname)
            party <- data[,4]
            votes <- data[,5:(ncol(data))]
            colnames(votes) <- paste("vote",1:ncol(votes))

            # print(legisname[cons1])
            # print(legisname[cons2])


            hr <- rollcall(votes,yea=1,nay=6,missing=0,notInLegis=9,
             legis.names=NULL, vote.names=NULL, legis.data=cbind(legisname,partyname,party), vote.data=NULL,
             desc=NULL, source=NULL)

            #print(hr) # used all 169 here.. 

            #result1 <- oc(hr, dims=1, minvotes=20, lop=0.025, polarity=c(135), verbose=F)          # 2 dims seems to cover this well.
            result2 <- oc(hr, dims=2, minvotes=20, lop=0.025, polarity=c(cons1,cons2), verbose=F)   #135 før
            #result3 <- oc(hr, dims=3, minvotes=20, lop=0.025, polarity=c(135,135,135), verbose=F) 

            #legislator.results <- na.omit(result2$legislators) # remove na.omit so all vectors are equal length
            legislator.results <- result2$legislators

            legisname <- legislator.results[,1]
            legisname <- as.character(legisname)
            partyname <- legislator.results[,2]
            partyname <- as.character(partyname)
            partycode <- legislator.results[,3]
            oc1 <- legislator.results[,10]
            oc2 <- legislator.results[,11]

            #suma <- summary(result2)
            #print(suma)

            calculated_values <- list("legisname" = legisname, "partyname" = partyname, "partycode" = partycode, "oc1" = oc1, "oc2" = oc2, "raw_result" = result2)
            # print(calculated_values)
            return(calculated_values)
        }
        
        ''')

        # assign np arry to r (a data.frame I assume.. )
        r.assign('r_data_list', np_data_list)

        # find the most rad reps from last go, use 167 if not in list
        try:
            analyse =  Wnominateanalyser.objects.all().order_by("-id")[0]       # print analyse.id
            # conservative_1D = Wnominateanalyserposisjoner.objects.all().filter(analyse=analyser.id).aggregate(Max('x'))
            # conservative_2D = Wnominateanalyserposisjoner.objects.all().filter(analyse=analyser.id).aggregate(Max('y'))
            conservative_1D = Wnominateanalyserposisjoner.objects.filter(analyse=analyse.id).order_by('-x')[0]
            conservative_2D = Wnominateanalyserposisjoner.objects.filter(analyse=analyse.id).order_by('-y')[0]

            # print "Debug: disse folk er mest rad"
            # print conservative_1D.representant.id, conservative_2D.representant.id
            # print "sjekk at det er rett folk:"
            # print data_list[int(np.where(np_data_list==conservative_1D.representant.id)[0][0])]
            # print data_list[int(np.where(np_data_list==conservative_2D.representant.id)[0][0])]    

            # overvrite variables: (aka finner posisjonen i rekken av folk)
            conservative_1D =  int(np.where(np_data_list==conservative_1D.representant.id)[0][0])
            conservative_2D =  int(np.where(np_data_list==conservative_2D.representant.id)[0][0])
            # print "finn deres posisjon i dataen:"
            #print conservative_1D, conservative_2D  #this is the position of the most rad peeps from last go

        except: # IndexError:
            # this cathes all possible odd stuff, should be logged... realy. 
            conservative_1D = 135 # as Cristohp dosnt know norwegian politics, I excpect this to be random
            conservative_2D = 135 # as Cristohp dosnt know norwegian politics, I excpect this to be random  
            print "NB: using backup conservatives"

        # make conservatives r-variables
        r.assign('r_conservative_1D', conservative_1D+1)    # add one for non 0-indexed r-lists?
        r.assign('r_conservative_2D', conservative_2D+1)    # distorts the first time around guy, but he's random anyhow.. 
        # run function
        
        a = r('calculate_oc_values(r_data_list, r_conservative_1D, r_conservative_2D)')
        

        # convert numeric person to real person object
        #print     # python object is 0-indexed..
        conservative_1D = Personer.objects.get(id=data_list[conservative_1D][0])
        conservative_2D = Personer.objects.get(id=data_list[conservative_2D][0])

        # create 1 Wnominateanalyse object and 169 posissjoner objects:
        
        correctly_classified = round(a[5][4][0]*100, 2)
        pre = round(a[5][4][1], 3)
        materiale = "Analysen er basert på de %s siste voteringene i Stortinget. " % self.number_of_votes
        w_analyse, created = Wnominateanalyser.objects.get_or_create(polarity1=conservative_1D, polarity2=conservative_1D, materiale=materiale, correctly_classified=str(correctly_classified), pre=str(pre))
        #print created # True if insert, false is update 


        # loop through results and create objects
        #print a
        # print type(a)
        # print a[0], len(a[0]), type(a[0])        
        # print a[0][0], len(a[0][0]), type(a[0][0])
        
        
        for mp in range(len(a[0])):
            #print type(a[0][mp])
            rep= Personer.objects.get(id=a[0][mp])
            # handle nans
            x = None if math.isnan(a[3][mp]) else str(a[3][mp])
            y = None if math.isnan(a[4][mp]) else str(a[4][mp])


            Wnominateanalyserposisjoner.objects.get_or_create(analyse=w_analyse, representant=rep, x=x, y=y)
#            print a[0][mp], a[1][mp], a[3][mp], a[4][mp]    # is x & y the correct once? believe so..



        # print type(a)   # <class 'rpy2.robjects.vectors.ListVector'>
        # print len(a), len(a[0])    #    6 169
        # print a[0][0], type(a[0]), len(a[0])    #BÅH <class 'rpy2.robjects.vectors.StrVector'> 169   
        # print a[1][0], type(a[1]), len(a[1])    #Fremskrittspartiet <class 'rpy2.robjects.vectors.StrVector'> 169
        # #print a[2].levels[a[2][0]-1], type(a[2]), len(a[2]) # partycode looks odd.. need lookup? -1 indeed         #200 <class 'rpy2.robjects.vectors.FactorVector'> 169
        # print a[3][0], type(a[3]), len(a[3])    # -0.631789554781 <class 'rpy2.robjects.vectors.FloatVector'> 169
        # print a[4][0], type(a[4]), len(a[4])    # 0.146948630795 <class 'rpy2.robjects.vectors.FloatVector'> 169


        # # from legislators
        # # legisname, coord1D, coord2D
        # print "legislators"
        # print type(a[0])

        # print "\nNytt forsøk \n"
        # # lage en liste for 
        # legislatorname = []
        # coord1D = []
        # coord2D = []
        # # så append i loopen under slik at 
        # #legis[13] er finner verdiene sine i coord1D[13]
        # #ok?
        # for name, vector in a[0].iteritems():   # a[0] is type rpy2.robjects.vectors.DataFrame can do .iteritems()
        #     print "name:"
        #     print name

        #     if name == "legisname":
        #     #  # jeg vil ha ting 0-indexert   #print len(vector.levels) # 169   #  print vector.levels[0] #  print vector.levels[168]
        #         for mp in vector:
        #             #print mp, vector[mp-1], vector[mp-1]-1, vector.levels[vector[mp-1]-1]
        #             legislatorname.append(vector.levels[vector[mp-1]-1])
        #             ## riktige = vector.levels[vector[mp-1]-1] ??
        #             #print type(mp) # int
        #         #print legislatorname, len(legislatorname)            
        #     if name == "coord1D":
        #         print "her er første dimensjon"
        #         for point in vector:
        #             coord1D.append(point)
        #         #print coord1D, len(coord1D)
        #     if name == "coord2D":
        #         print "her er andre dimensjon"
        #         for point in vector:
        #             coord2D.append(point)
        #         #print coord2D, len(coord2D)

        #     print vector
        #     print type(vector)
        #     print "\n\n"
        #     #print type(l) # tules 


        # # from rollcalls
        # # I discard good stuff, e.g. the vectors for each vote

        print "Number of dimensions: %s" % (int(a[5][2][0]))

        # # from fits
        # # classified right, PRE: 0.9930957 0.9794108
        print "fits: percent correct classiﬁcation: %s, APRE: %s" % (round(a[5][4][0]*100, 2), round(a[5][4][1], 3))


        # # polarity1, polarity2
        # # materiale
        # # correctly_classified
        # # pre


    def handle(self, *args, **options):
        
        # for person_id in args:
        #     print person_id

        #     # finn personen (skal alltid finnes)
        #     person = Personer.objects.get(pk=str(person_id))
        
        data = self.construct_dataset(self.number_of_votes) # returns dict of lists where text is in unicode..
        

        self.oc(data)
        self.stdout.write('Successfully computed OC from last %s votes\n' % (self.number_of_votes))


        














