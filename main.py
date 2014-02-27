#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import path_fix

import webapp2
import pytz
from BeautifulSoup import BeautifulSoup
import json
import urllib2
from pytz import timezone
from icalendar import Calendar, Event,  LocalTimezone
from datetime import datetime, timedelta
import logging


class caldict(dict):
    def pk(self):
        return self['uid']
   

def days_delta(n):
    return timedelta(days=n)


def cal_demo(queryset):
    cal = Calendar()    
    cal.add('version', '2.0')
    cal.add('prodid', '-//V and A upcoming events//www.vam.ac.uk.com/whatson/')
    cal.add('X-WR-CALNAME','V and A Events Calendar' )
    lt = LocalTimezone() # we append the local timezone to each time so that icalendar will convert
                         # to UTC in the output
    for ent in queryset:
        event = Event()
        event.add('summary', ent['event_name'])
        event.add('dtstart', datetime.combine(ent['event_date'],ent['start_time']).replace(tzinfo=lt))
        event.add('dtend', datetime.combine(ent['stop_date'],ent['stop_time']).replace(tzinfo=lt))
        event.add('dtstamp', ent['updated_on'].replace(tzinfo=lt))
        event['uid'] = ent.pk  # should probably use a better guid than just the PK
        event.add('description', ent['description'])
        cal.add_component(event)
    return cal.to_ical()

def get_first_int_in_list(src_list):
    for i in src_list:
        try:
            return(int(i))
        except ValueError:
            pass
            
def get_id_from_url(path):
    links_eles= path.split('/')
    return (get_first_int_in_list(links_eles))

def output_urls(idlist):
    r= ''
    for id in idlist:
	    r += '<li><a href="http://www.vam.ac.uk/whatson/event/%s/">%s</a></li>' % (id,id)
    r = '<ul>%s</ul>' % r    
    return r

class MainHandler(webapp2.RequestHandler):
    def get(self):
        for daycount in range(0,14):
            scandate = (datetime.now() + days_delta(daycount)).strftime("%Y%m%d")
            self.response.write('<h2>%s</h2>' % scandate )
            urlpath = "http://www.vam.ac.uk/whatson/json/events/day/%s/" % scandate
            response = urllib2.urlopen(urlpath)
            data = json.load(response)
            for d in data:
                if d['fields']['event_type'] not in [40, 41 , 45 ]:
                    continue
                if 'TOUR' in d['fields']['short_description']:
                    continue
                # self.response.write(d['fields'])
                self.response.write('<img src="http://www.vam.ac.uk/whatson/media/%s" style="width:250px;"><br>' % d['fields']['image'])
                for f in ['name','first_slot','last_slot', 'short_description','event_type',
                          'free','image']:
                    self.response.write('%s: %s' % (f, d['fields'][f]))
                    dur = datetime.strptime(d['fields']['last_slot'], '%Y-%m-%d %H:%M:%S') - datetime.strptime(d['fields']['first_slot'], '%Y-%m-%d %H:%M:%S')
                    self.response.write('<br>' )
                    pass
                self.response.write('<br>duration: %s' % dur )
                # if dur > timedelta(days=5):
                #     self.response.write('<br>long event!' )
                self.response.write('<hr>')


class CalHandler(webapp2.RequestHandler):
    def get(self):
        qs = []
        for daycount in range(0,31):
            scandate = (datetime.now() + days_delta(daycount)).strftime("%Y%m%d")
            # self.response.write('<h2>%s</h2>' % scandate )
            urlpath = "http://www.vam.ac.uk/whatson/json/events/day/%s/" % scandate
            response = urllib2.urlopen(urlpath)
            data = json.load(response)
            for d in data:
                if d['fields']['event_type'] not in [40, 41 , 45 ]:
                    continue
                if 'tour' in d['fields']['short_description'].lower():
                    continue
                if 'tour' in d['fields']['name'].lower():
                    continue
                dur = datetime.strptime(d['fields']['last_slot'], '%Y-%m-%d %H:%M:%S') - \
                      datetime.strptime(d['fields']['first_slot'], '%Y-%m-%d %H:%M:%S')
                if dur > timedelta(days=5):
                    continue

                e1 = caldict()
                e1['uid'] = d['fields']['peo_code']
                e1['event_name'] = d['fields']['name']
                logging.info(e1['event_name'])
                logging.info('dur %s' % dur)
                logging.info(d['fields']['first_slot'])
                logging.info(d['fields']['last_slot'])
                e1[	'event_date'] = datetime.strptime(d['fields']['first_slot'], '%Y-%m-%d %H:%M:%S')
                e1[	'description'] = d['fields']['long_description']
                e1[	'start_time'] =datetime.strptime(d['fields']['first_slot'], '%Y-%m-%d %H:%M:%S').time()
                e1[	'stop_date'] = datetime.strptime(d['fields']['last_slot'], '%Y-%m-%d %H:%M:%S')
                e1[	'stop_time'] =datetime.strptime(d['fields']['last_slot'], '%Y-%m-%d %H:%M:%S').time()
                if e1['start_time'] == e1[	'stop_time']:
                    logging.info('no duration')

                    e1[	'stop_time'] = (e1['stop_date'] + timedelta(hours=1)).time()
                e1[	'updated_on'] =datetime.now()

                qs.append(e1)
        self.response.write(cal_demo(qs))


app = webapp2.WSGIApplication([
    ('/cal', CalHandler),
    ('/ical', CalHandler),
    ('.*', MainHandler)
], debug=True)
