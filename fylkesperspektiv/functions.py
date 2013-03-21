#!/usr/bin/python
# encoding: utf-8
from samstemmer.fylkesperspektiv.models import Sesjoner

def get_stopwords():
    stop_word_lines = open("samstemmer/fylkesperspektiv/stop2.txt", "r")
    stop_words = []
    for word in stop_word_lines:
        stop_words.append(unicode(word.strip().lower(), 'utf8'))            # end of line chars are included. does strip() removed those??
    return stop_words


def font_size_from_percent(value):
    ''' sizes set with css later, but here's the dist '''
    #print value
    #print type(value)
    font_size = 1
    if value > 99: font_size = 1 
    elif value < 99 and value > 80: font_size = 2
    elif value < 80 and value > 70: font_size = 3
    elif value < 70 and value > 60: font_size = 4
    elif value < 60 and value > 50: font_size = 5
    elif value < 50 and value > 40: font_size = 6
    elif value < 40 and value > 30: font_size = 7
    elif value < 30 and value > 20: font_size = 8
    elif value < 20 and value > 10: font_size = 9
    elif value > 10: font_size = 10
    return font_size

def get_current_session_nr():
    sesjon = Sesjoner.objects.get(er_innevaerende=True)
    return sesjon

# dette er fra http://docs.python.org/2/library/csv.html#examples csv modulen støtter ikke UTF8!!
import csv, codecs, cStringIO

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
