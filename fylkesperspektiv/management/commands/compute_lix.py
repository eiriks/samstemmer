#!/usr/bin/python
# encoding: utf-8

from django.core.management.base import BaseCommand #, CommandError
from fylkesperspektiv.models import Lix, Personer, Sporsmal, Representanter
#from nltk_contrib.readability.textanalyzer import textanalyzer
import textanalyzer_no  # my rewritten module
from optparse import make_option

from decimal import *   # http://modeldev.blogspot.no/2009/10/django-cannot-convert-float-to-decimal.html
def LIX(text = ''):
    lang = "no"
    t = textanalyzer_no.Textanalyzer(lang)
    #t.analyzeText(text)
    orda = t.analyzeText(text)    #print orda
    analyzedVars = orda         #.analyzedVars      #print analyzedVars
    score = 0.0
    longwords = 0.0
    for word in analyzedVars['words']:
        if len(word) >= 7:
            longwords += 1.0
    score = analyzedVars['wordCount'] / analyzedVars['sentenceCount'] + float(100 * longwords) / analyzedVars['wordCount']
    return score

class Command(BaseCommand):
    #args = '<poll_id poll_id ...>'
    help = '''Compute LIX for person IDs, commited as "./manage.py compute_lix est eso jst"
    to get all the first time, run "./manage.py compute_lix --all"'''
    option_list = BaseCommand.option_list + (
        make_option('--all',
            action='store_true',
            dest='bootstrap',
            default=False,
            help='Get all insted of just a few'),
        )

    def handle(self, *args, **options):
        print args, options
        #print LIX(text2)
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
                #print type(person_id)              # find person - should always be here
                
                person = Personer.objects.get(pk=str(person_id.encode('utf8'))) 
                # create lix object (and a true/false for if it existed)

                # feiler da auto inc id på lix aldri matcher 
                #lix, created = Lix.objects.get_or_create(person=person,materiale='temp_materiale',value=10)
                #print created, lix

                text = Sporsmal.objects.filter(sporsmal_fra=person).filter(type="skriftlig_sporsmal").values("tittel")
                only_text = " ".join(x['tittel'] for x in text)# <- dette kommer som unicode .decode('utf-8')#.encode("utf-8") 
                materiale = "%s skriftlige spørsmål" % (len(list(x for x in text)))     # print materiale
                #print only_text, len(only_text)

                if len(only_text)>0:
                    lix_value = LIX(only_text)   
                    lix_value = Decimal(str(lix_value))
                    
                    #print lix_value

                    try:
                        lix = Lix.objects.get(person=person)
                        lix.materiale = materiale
                        lix.value = lix_value
                    except Lix.DoesNotExist:
                        lix = Lix(person=person)
                        lix.materiale = materiale
                        lix.value = lix_value         
                    lix.save()
                    self.stdout.write('Successfully updated lix score for "%s: %s -basert på %s"\n' % (person_id.encode("utf8"), lix.value, lix.materiale))
                else:
                    self.stdout.write('Ikke nok materiale på %s\n' % (person_id.encode("utf8"))) 
