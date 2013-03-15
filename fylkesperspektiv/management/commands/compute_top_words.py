#!/usr/bin/python
# encoding: utf-8

from django.core.management.base import BaseCommand #, CommandError
from fylkesperspektiv.models import Personer, Sporsmal, Representanter

import nltk
from collections import defaultdict
from optparse import make_option

import textanalyzer_no                  # my rewritten module
from fylkesperspektiv import functions  # dette er min function.py fil


def question_queryset_to_unicode_text(queryset):
    lang = "no"
    t = textanalyzer_no.Textanalyzer(lang)
    pure_words = t.getWords(" ".join([te['tittel'] for te in queryset]))
    pure_words = [w for w in pure_words if w not in ['', ' ', '" ', ' "', '"', '\n']]
    return pure_words

def create_weigted_list(queryset):
    ''' create a weigthed list of top word from questions from a particular user '''
    # first get a list of stop words
    stopwords = functions.get_stopwords()
    pure_words = question_queryset_to_unicode_text(queryset)

    counts = defaultdict(int)
    for word in pure_words:
        if word.lower() not in stopwords:
            counts[word] += 1
    
    pairs = [(x,y) for x,y in counts.items() if y >= 3]                             # remove shorter than 3 accounts
    if len(pairs) > 1:
        # if we have data to work with:                                             
        sorted_stems = sorted(pairs, key = lambda x: x[1], reverse=True)[:30]       # Sort (stem,count) pairs based on count, pick top n words
        max_value = sorted_stems[0][1]                                              # max_value, min_value = sorted_stems[0][1], sorted_stems[-1][1]
        #print sorted_stems, max_value
        result = [{'tag': x,  'freq': y, 'size': functions.font_size_from_percent(round(float(y)/max_value*100,2)) } for x, y in sorted_stems]       # round(n,2) <- rounds off float.
    else:
        # too little data to do this
        result = [{'tag': 'for lite data til å lage ordsky', 'freq': 0, 'size': 7}]
    return result

def top_tfidf_words(queryset_person, document_collection):
    stopwords = functions.get_stopwords()
    # fast way to join lists: http://stackoverflow.com/questions/716477/join-list-of-lists-in-python
    person_words = question_queryset_to_unicode_text(queryset_person) #list(itertools.chain.from_iterable([tokenizer.tokenize(question.tittel) for question in queryset_person]))  # wordpunct_tokenize ser ut til å fungere bedre enn mange andre. men en regexp er bedre?
     #list(itertools.chain.from_iterable([tokenizer.tokenize(question.tittel) for question in queryset_everybody]))

    evaluated_words = {}                                # dict to hold words

    #print "evaluerer ord"
    if len(person_words) > 30:
        #print len(set(person_words))
        for word in set(person_words):                      # just once for each word
            #print "ord: %s og value %s" % (word, dc.tf_idf(word, person_words))
            if word.lower() not in stopwords:                   # får ord som har, få, som top.. prøver med stoppord
                evaluated_words[word] = document_collection.tf_idf(word, person_words)
        #print evaluated_words
        sorted_words = sorted(evaluated_words.items(), key=lambda x: x[1], reverse=True)[:29]
        max_tfidf = sorted_words[0][1]
        result = [{'tag': x, 'tfidf': y, 'size': functions.font_size_from_percent(round(float(y)/max_tfidf*100,2)) } for x, y in sorted_words]
    else:
        result = [{'tag': 'for lite data til å lage ordsky', 'tfidf': 0, 'size': 7}]
    return result


class Command(BaseCommand):
    #args = '<poll_id poll_id ...>'
    help = """Compute top word from perspn './manage.py compute_top_words est eso jst'
    tfidf is slow, so compute at apropriate times...  
    """
    option_list = BaseCommand.option_list + (
    make_option('--all',
        action='store_true',
        dest='bootstrap',
        default=False,
        help='Get all insted of just a few'),
    )

    def handle(self, *args, **options):

        # create documen_collection of all questions..
        queryset_everybody = Sporsmal.objects.all().values("tittel") # slow, so only do once..
        everybodys_words = question_queryset_to_unicode_text(queryset_everybody)
        document_collection = nltk.TextCollection(everybodys_words)          # create nltk object
        print "created document collection"

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
                #print person_id

                # finn personen (skal alltid finnes)
                person = Personer.objects.get(pk=person_id)
                # finn teksten i tittlene på spørsmål personen har stillt
                text = Sporsmal.objects.filter(sporsmal_fra=person).values("tittel")

                # create html "tag cloud" of top freq words
                freq_words = create_weigted_list(text)
                frequent_words = []
                for word in freq_words:
                        frequent_words.append('<span class="size-'+ str(word['size']) +'" name="antall: '+ str(word['freq']) +'">'+ word['tag']+'</span>')
                freq_words = ''.join(frequent_words)

                # create html "tag cloud" of top tfidf words (given persons words and a document collection)
                tfidf = top_tfidf_words(text,document_collection)
                tfidf_words = []
                for word in tfidf:
                    tfidf_words.append('<span class="size-'+ str(word['size']) +'" name="tfidf: '+ str(word['tfidf']) +'">'+ word['tag']+'</span>')
                tfidf = ''.join(tfidf_words)

                # save the newly computed html
                person.top_words_in_questions = freq_words
                person.top_tfidf_words_in_questions = tfidf
                person.save()
                #print freq_words, tfidf
                self.stdout.write('Successfully computed words for: "%s" \n' % (person_id))
        else:
            print "ingen personer? prøv å sende med -aa for å ta alle.."




