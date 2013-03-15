# encoding: utf-8
from django import template
from django.utils.translation import ungettext, ugettext
import datetime

register = template.Library()

@register.filter    
def subtract(value, arg):
    return value - arg

@register.filter(name='percentage')  
def percentage(fraction, population): 
	print fraction, population
	try:
		return "%.2f%%" % ((float(fraction) / float(population)) * 100)  
	except ValueError:
		return ''  

@register.filter
def stip_underscore(word):
	word = word.split("_")
	return u" ".join([n for n in word])


@register.filter
def lixcategory(value):
	u""" http://sv.wikipedia.org/wiki/LIX
	LIX-tal för texter av olika slag
	- 25	Barnböcker.
	25 - 30	Enkla texter.
	30 - 40	Normaltext / skönlitteratur.
	40 - 50	Sakinformation, till exempel Wikipedia.
	50 - 60	Facktexter.
	över 60	Svåra facktexter / forskning / avhandlingar."""

	value = round(float(value),1)		# ensure a float 
	catname = ''						# set empty
	if value > 60:
		catname = 'avhandling'
	elif (value > 50 and value <= 60):
		catname = 'fagtekst'
	elif value > 40 and value <= 50:
		catname = 'sakinformation'
	elif value > 30 and value <= 40:
		catname = 'normaltekst'
	elif value > 25 and value <= 30:
		catname = 'lettlest'
	elif value <= 25:
		catname = 'barnebok'
	else:
		catname = 'ukategorisert'
	return catname

@register.filter
def tid_siden(d, now=None): 
	""" Takes two datetime objects and returns the time between d...
    fra : http://docs.nullpobug.com/django/trunk/django.utils.timesince-pysrc.html#timesince 
    Adapted from http://blog.natbat.co.uk/archive/2003/Jun/14/time_since 	""" 
	chunks = ( 
	(60 * 60 * 24 * 365, lambda n: ungettext(u'år', u'år', n)), 
	(60 * 60 * 24 * 30, lambda n: ungettext(u'måned', u'måneder', n)), 
	(60 * 60 * 24 * 7, lambda n : ungettext('uke', 'uker', n)), 
	(60 * 60 * 24, lambda n : ungettext('dag', 'dager', n)), 
	(60 * 60, lambda n: ungettext('time', 'timer', n)), 
	(60, lambda n: ungettext('minutt', 'minutter', n)) 
	)
	# Convert datetime.date to datetime.datetime for comparison. 
	if not isinstance(d, datetime.datetime): 
		d = datetime.datetime(d.year, d.month, d.day) 
	if now and not isinstance(now, datetime.datetime): 
		now = datetime.datetime(now.year, now.month, now.day) 

	if not now: 
	  if d.tzinfo: 
	      now = datetime.datetime.now(LocalTimezone(d)) 
	  else: 
	      now = datetime.datetime.now() 

	# ignore microsecond part of 'd' since we removed it from 'now' 
	delta = now - (d - datetime.timedelta(0, 0, d.microsecond)) 
	since = delta.days * 24 * 60 * 60 + delta.seconds 
	if since <= 0: 
	  # d is in the future compared to now, stop processing. 
	  return u'0 ' + ugettext('minutter') 
	for i, (seconds, name) in enumerate(chunks): 
	  count = since // seconds 
	  if count != 0: 
	      break 
	s = ugettext('%(number)d %(type)s') % {'number': count, 'type': name(count)} 
	if i + 1 < len(chunks): 
	  # Now get the second item 
	  seconds2, name2 = chunks[i + 1] 
	  count2 = (since - (seconds * count)) // seconds2 
	  if count2 != 0: 
	      s += ugettext(', %(number)d %(type)s') % {'number': count2, 'type': name2(count2)} 
	return s 

