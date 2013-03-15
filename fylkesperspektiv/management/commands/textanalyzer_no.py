#!/usr/bin/python
# encoding: utf-8


from nltk.tokenize import *
import nltk.data
import syllables_no


class Textanalyzer(object):
    """Except a -> unicode <- string of text
    based on: https://github.com/nltk/nltk_contrib/tree/master/nltk_contrib/readability
    rewritten to work with unicode text 
    """
    tokenizer = RegexpTokenizer('(?u)\W+|\$[\d\.]+|\S+')
    special_chars = ['.', ',', '!', '?']

    def __init__(self, lang):
        self.lang = lang

    def setLang(self,lang):
        self.lang = lang

    def analyzeText(self, text=''):
        if text != '':            #if text != self.text:
        #    lang = "no"
            words = self.getWords(text)
            # ??
            charCount = self.getCharacterCount(words)
            # # antall ord
            wordCount = len(words) # denne trenger jeg
            # # antall setninger
            sentenceCount = len(self.getSentences(text)) # denne trenger jeg
            # # stavelser totalt ??
            syllableCount = self.countSyllables(words)
            # # komplekse ord
            complexwordsCount = self.countComplexWords(text)
            # # ord pr setning
            averageWordsPerSentence = wordCount/sentenceCount

            analyzedVars = {}
            analyzedVars['words'] = words
            analyzedVars['charCount'] = float(charCount)
            analyzedVars['wordCount'] = float(wordCount)
            analyzedVars['sentenceCount'] = float(sentenceCount)
            analyzedVars['syllableCount'] = float(syllableCount)
            analyzedVars['complexwordCount'] = float(complexwordsCount)
            analyzedVars['averageWordsPerSentence'] = float(averageWordsPerSentence)
            return analyzedVars

    def getWords(self, text=''):
        words = []                  #print type(text)    # unicode 
        words = self.tokenizer.tokenize(text)
        filtered_words = []
        for word in words:
            if word in self.special_chars or word == " ":
                pass
            else:
                new_word = word.replace(",","").replace(".","")
                new_word = new_word.replace("!","").replace("?","")
                filtered_words.append(new_word)
        return filtered_words

    def getCharacterCount(self, words):
        characters = 0
        for word in words:          #print word, type(word), len(word) # as unicode, this is right
            characters += len(word) #len(word.decode("utf-8"))
        return characters

    def getSentences(self, text=''):
        sentences = []
        tokenizer = nltk.data.load('tokenizers/punkt/english.pickle') # didnt exspect this to work..
        sentences = tokenizer.tokenize(text)
        return sentences

    def countSyllables(self, words = []):
        if self.lang == "unknown":
            print "WARNING: Unknown language, using Norwegian\n"
            self.lang = "no"        
        syllableCount = 0
        syllableCounter = {}
        #syllableCounter['eng'] = syllables_en.count
        syllableCounter['no'] = syllables_no.count
        for word in words:
            #print word, syllableCounter[self.lang](word) # ser rett ut.
            syllableCount += syllableCounter[self.lang](word)
        return syllableCount

    def countComplexWords(self, text=''):
        words = self.getWords(text)
        sentencesList = self.getSentences(text);
        complexWords = 0
        found = False;
        curWord = []
        
        for word in words:          
            curWord.append(word)
            if self.countSyllables(curWord)>= 3:
                #Checking proper nouns. If a word starts with a capital letter
                #and is NOT at the beginning of a sentence we don't add it
                #as a complex word.
                if not(word[0].isupper()):
                    complexWords += 1
                    #print word, " er komplekst 1"
                else:
                    for sentence in sentencesList:
                        if sentence.startswith(word):
                        #if str(sentence).startswith(word):
                            found = True
                            break
                    if found: 
                        complexWords+=1
                        #print word, " er komplekst 2"
                        found = False
            curWord.remove(word)
        return complexWords