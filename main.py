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

import urllib2
from pytz import timezone
from icalendar import Calendar, Event,  LocalTimezone
from datetime import datetime, timedelta


class caldict(dict):
    def pk(self):
        return 123
   

def days_delta(n):
    return timedelta(days=n)


        
def cal_demo():    
    cal = Calendar()    
    cal.add('version', '2.0')
    cal.add('prodid', '-//test file//example.com//')
    cal.add('X-WR-CALNAME','Test Calendar' )
    lt = LocalTimezone() # we append the local timezone to each time so that icalendar will convert
                         # to UTC in the output
    e1 = caldict()
    
    e1['uid'] = 1
    e1['event_name'] ='eve1'
    e1[	'event_date'] =datetime.now() + days_delta(1)
    e1[	'start_time'] =datetime.now().time()
    e1[	'stop_date'] =datetime.now() + days_delta(2)
    e1[	'stop_time'] =datetime.now().time()
    e1[	'updated_on'] =datetime.now()
    queryset = [e1]	    
    for ent in queryset:        
        event = Event()
        event.add('summary', ent['event_name'])
        event.add('dtstart', datetime.combine(ent['event_date'],ent['start_time']).replace(tzinfo=lt))
        event.add('dtend', datetime.combine(ent['stop_date'],ent['stop_time']).replace(tzinfo=lt))
        event.add('dtstamp', ent['updated_on'].replace(tzinfo=lt))
        event['uid'] = ent.pk  # should probably use a better guid than just the PK
        event.add('priority', 5)
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
        for daycount in range(0,4):
            scandate = (datetime.now() + days_delta(daycount)).strftime("%Y%m%d")
            self.response.write('<h2>%s</h2>' % scandate )
            urlpath = "http://www.vam.ac.uk/whatson/events/day/%s/" % scandate
            url = urllib2.urlopen(urlpath)
            self.response.write(urlpath )
            self.response.write('<br>' )
            content = url.read().decode('utf-8', 'strict').encode('ascii', 'ignore')
            soup = BeautifulSoup(content.decode('utf-8', 'ignore'))
            div = soup.find('div', {'id':'etype_free-talks-tours'})
            try:
                aa_div = div.findAll('a')
                links = [a['href'].strip() for a in aa_div]
                ids = set([get_id_from_url(ele) for ele in links])
                self.response.write(output_urls(ids))
                self.response.write('---')
            except AttributeError:
               self.response.write('<br>??<br>')



app = webapp2.WSGIApplication([
    ('.*', MainHandler)
], debug=True)
