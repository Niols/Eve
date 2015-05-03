#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import caldav
from datetime import datetime, timedelta
from urllib.parse import urlparse

VDATE_FMT = '%Y%m%d'
"Date format in VEVENTs."

VTIME_FMT = '%H%M%S'
"Time format in VEVENTs."

VDATETIME_FMT = VDATE_FMT + 'T' + VTIME_FMT
"Datetime format in VEVENTs."

DEFAULT_HTTP_PORT = 80
"Default port for http URLs."



def parse_dt(dt_str):
    """
    Takes a time formated as datetimes in VEVENTs and return a proper datetime
    (or date, depending on the format).
    """
    if dt_str[-1].upper() == 'Z': print('caca')
    try: return datetime.strptime(dt_str, VDATE_FMT+'T'+VTIME_FMT+'%Z')
    except ValueError: return datetime.strptime(dt_str, VDATE_FMT).date()



def rebuild_url(url, with_logs=False, username=None, password=None, with_port=False, port=None):
    """
    Reconstructs an URL 
    """

    url = urlparse(url)

    if with_logs:
        if (url.username or username) and (url.password or password):
            logs = '%s:%s@' % ( username if username else url.username ,
                                password if password else url.password )
        else:
            raise Exception('with_logs can\'t be True if no username or password is given.')
    else:
        logs = ''

    if with_port:
        if (url.port or port):
            port = ':%s' % ( port if port else url.port ,)
        else:
            raise Exception('with_port can\'t be True if no port is given.')
    else:
        port = ''
        
    return '%s://%s%s%s%s' % (url.scheme, logs, url.hostname, port, url.path)



def get_calendar(url, username=None, password=None):
    """
    Returns the CalDAV calendar found behind the given URL.
    Logs can be given to this function or in the URL.
    """
    
    davclient_url = rebuild_url(url,
                                with_logs=True, username=username, password=password,
                                with_port=True, port=DEFAULT_HTTP_PORT)
    davclient = caldav.DAVClient(davclient_url)

    calendar_url = rebuild_url(url, with_logs=False, with_port=True, port=DEFAULT_HTTP_PORT)

    try:
        return [c for c in davclient.principal().calendars()
                if c.url.rstrip('/') == calendar_url.rstrip('/')][0]
    except:
        raise Exception('Calendar `%s` does not exist.' % url)


