#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from frontircbot import FrontIRCBot
import caldavclient
import sched
import time as mod_time
from datetime import datetime, date, timedelta, time
import json
import sys


if len(sys.argv) != 2:
    print('Usage: %s <config-file>' % (sys.argv[0],))
    sys.exit(1)


config = json.load(open(sys.argv[1], 'r'))
bindings = config['bindings']


Eve = FrontIRCBot(bindings['nickname'])


def print_tomorrows_events():
    tomorrow = date.today()+timedelta(1)

    for binding in bindings:
        calendar = caldavclient.get_calendar(binding['caldav']['url'], binding['caldav']['username'], binding['caldav']['password'])
        events = calendar.date_search(tomorrow, tomorrow+timedelta(1))
        if not events:
            message = 'No events planned for tomorrow (%s).' % str(tomorrow)
        else:
            message = 'Events for tomorrow (%s):' % str(tomorrow)
            for event in events:
                vevent = event.instance.vevent
                message += '\n  %s (%s)' % ( vevent.summary.value ,
                                             vevent.dtstart.value )
        Eve.privmsg(binding['irc']['server'], binding['irc']['target'], message)


def repeat_everyday(func, args=()):
    print('repeat_everyday')
    scheduler.enter(86400, 1, repeat_everyday, (func,args))
    func(*args)


def datetime_timestamp(dt):
    "This corresponds to python3's datetime.timestamp() method."
    return mod_time.mktime(dt.timetuple()) + dt.now().microsecond / 1e6
    

first_run = datetime.combine(date.today(), time(22,0))
first_run = first_run if first_run > datetime.now() else first_run + timedelta(1)

scheduler = sched.scheduler(mod_time.time, mod_time.sleep)
scheduler.enterabs(datetime_timestamp(first_run), 1, repeat_everyday, (print_tomorrows_events,))
scheduler.run()
