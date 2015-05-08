#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from frontircbot import FrontIRCBot, Control, Color
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

for binding in bindings:
    for caldav in binding['caldavs']:
        caldav['calendar'] = caldavclient.get_calendar(caldav['url'], caldav['username'], caldav['password'])


Eve = FrontIRCBot(config['nickname'])


def print_tomorrows_events():
    tomorrow = date.today()+timedelta(1)

    for binding in bindings:
        events = []
        for caldav in binding['caldavs']:
            events += caldav['calendar'].date_search(tomorrow, tomorrow+timedelta(1))
        vevents = [event.instance.vevent for event in events]
        vevents.sort(key = lambda vevent: vevent.dtstart.valueRepr())

        print(vevents)

        if not vevents:
            message = 'No events planned for tomorrow (%s).' % str(tomorrow)
        else:
            message = Control.Color + Color.Red + 'Events for tomorrow (%s):' % str(tomorrow)
            for vevent in vevents:
                if hasattr(vevent.dtstart.value, 'hour') and hasattr(vevent.dtstart.value, 'minute'):
                    message += '\n' + Control.Color + Color.Gray
                    message += '{:>2}:{:0>2}'.format( vevent.dtstart.value.hour,
                                                      vevent.dtstart.value.minute )
                    message += Control.Reset + '  ' + vevent.summary.value
                else:
                    message += '\n       ' + vevent.summary.value
        Eve.privmsg(binding['irc']['server'], binding['irc']['target'], message)


def repeat_everyday(func, args=()):
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
